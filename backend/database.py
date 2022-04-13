import calendar
import json
import requests
from bs4 import BeautifulSoup
from itertools import groupby

from backend import paths

 
api_url: str = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
version: int = 1


def verify_and_update() -> None:
    if not paths.db_path.is_file() or get_data()["version"] != version:
        update()

def filter_sets_and_return_attributes(name: str, sets: list = None) -> list:
    sets = sets or get_sets()
    sets_filtered = filter_list_by_name(sets, name)

    return [
        {
            "name": set_name,
            "date": sets[set_name]["date"],
            "type": sets[set_name]["type"]
        } for set_name in sets_filtered
    ]


def filter_cards_by_name(name: str) -> list:
    return list(filter_list_by_name(get_cards("name"), name))


def filter_sets_by_name(name: str) -> list:
    return list(filter_list_by_name(get_sets(), name))


def get_card_id(card_name: str) -> int:
    matches: list = [card["id"] for card in get_cards().values() if card["name"] == card_name]
    return (matches or [None])[0]


def get_cards_from_sets(set_names: set) -> list:
    sets: dict = get_sets()
    cards: list = []

    for set_name in set_names:
        cards = cards + sets[set_name]["cards"]

    return list(set(cards))


def get_set_types(sets: list = None) -> list:
    sets = sets or get_sets()
    types = list({product["type"] for product in sets.values()})
    types.sort()
    return types


def get_cards(attribute: str = None) -> dict:
    cards: dict = get_data()["cards"]

    if attribute:
        return list(map(
            lambda card: card[attribute],
            cards.values()
        ))
    else:
        return cards


def get_sets() -> list:
    return get_data()["sets"]


def get_data() -> dict:
    with open(paths.db_path, "r") as file:
        data = file.read()

    return json.loads(data)


# ignores case (A -> a)
def filter_list_by_name(strings: list, name: str) -> filter:
    name = name.lower()

    return filter(
        lambda string: name in string.lower(),
        strings
    )


def update() -> None:
    response = requests.get(api_url)

    if response.status_code != 200:
        raise ResponseStatusError(reponse.status_code)

    response_json: dict = response.json()
    del response

    cards: dict = _extract_cards_from_response(response_json)
    card_sets: dict = _extract_sets_from_response(response_json)
    del response_json

    card_database = json.dumps({
        "version": version,
        "cards": cards,
        "sets": card_sets
    })

    del cards

    # write database to storage
    with open(paths.db_path, "w") as file:
        file.write(card_database)


def _extract_cards_from_response(response_json: dict) -> dict:
    return {
        card["id"]: {
            "id": card["id"],
            "name": card["name"],
            "type": card["type"],
        } for card in response_json["data"] if card.get("card_sets")
    }


def _extract_sets_from_response(response_json: dict) -> dict:
    product_release_dates: dict = _get_product_release_dates_from_yugipedia()

    card_sets: dict = dict()
    for card in response_json["data"]:
        for card_set in card.get("card_sets", []):
            card_sets[card_set["set_name"]] = card_sets.get(card_set["set_name"], {"cards": []})
            card_sets[card_set["set_name"]]["cards"] = [card["id"], *card_sets[card_set["set_name"]]["cards"]]

    card_sets["2020 Tin of Lost Memories"] = card_sets.pop("2020 Tin of Lost Memories Mega Pack")

    # remove unneeded sets
    to_delete: list = []

    for set_name in card_sets:
        if len(card_sets[set_name]["cards"]) < 15:
            to_delete.append(set_name)
        else:
            card_sets[set_name]["date"] = product_release_dates.get(set_name)

    for set_name in to_delete:
        del card_sets[set_name]

    # rename tins
    for tin in ["2020 Tin of Lost Memories", "2021 Tin of Ancient Battles"]:
        card_sets[f"{tin} Mega Pack"] = card_sets.pop(tin)

    # add categories to sets
    category: dict = _get_sets_by_category()
    for set_name in card_sets:
        card_sets[set_name]["type"] = category.get(set_name, "Misc.")

    # add categories without https requests
    def change_category_generic(category: str, name: str = None) -> None:
        for set_name in filter_list_by_name(card_sets, category):
            if category in set_name:
                card_sets[set_name]["type"] = name or category

    # hidden arsenal
    for set_name in filter_list_by_name(card_sets, "hidden arsenal"):
        if set_name[14:15] != ":":
            card_sets[set_name]["type"] = "Hidden Arsenal"

    change_category_generic("Duelist Pack")
    change_category_generic("Legendary Duelists")
    change_category_generic("Mega Pack")
    change_category_generic("Tournament Pack")
    change_category_generic("Turbo Pack")
    change_category_generic("Astral Pack")
    change_category_generic("OTS Tournament Pack", "OTS Pack")
    change_category_generic("(POR)", "OTS Pack Portugal")
    change_category_generic("Structure Deck")
    change_category_generic("Starter Deck")
    change_category_generic("God Deck", "Starter Deck")
    change_category_generic("Speed Duel")  # includes starter decks and tournament packs

    # gold series
    for set_name in filter_list_by_name(card_sets, "gold"):
        if card_sets[set_name]["type"] == "Misc.":
            card_sets[set_name]["type"] = "Gold Series"

    return card_sets


def _get_sets_by_category() -> dict:
    def get_soup(url: str) -> BeautifulSoup:
        response: requests.Response = requests.get(url)
        return BeautifulSoup(response.content, "html.parser")

    set_category: dict = {}

    soup = get_soup("https://yugipedia.com/wiki/Core_Booster")
    tbody = soup.find_all("tbody")
    for index, set_group in enumerate(tbody[3].find_all("tr")[1:] + tbody[4].find_all("tr")[1:]):
        for set_name in set_group.find_all("a")[index != 0:]:
            set_category[set_name.get("title")] = "Core Booster"

    soup = get_soup("https://yugipedia.com/wiki/Deck_Build_Pack")
    tbody = soup.find_all("tbody")
    for set_name in tbody[2].find_all("a"):
        set_category[set_name.get("title")] = "Deck Build Pack"

    return set_category


def _get_product_release_dates_from_yugipedia() -> dict:
    month_number: dict = _get_month_name_to_number_dict()

    # the edit view makes it easier to separate information 
    # and makes it possible to only work with TCG sets from the start
    url: str = "https://yugipedia.com/wiki/Order_of_Set_Release?action=edit&section=305"
    response: requests.Response = requests.get(url)

    print(response.status_code)

    soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

    text_area: str = soup.find("textarea").string
    text_area = [line for line in text_area.split("\n") if line != ""][1:]

    def remove_characters(string: str, *characters: str) -> str:
        for character in characters:
            string = string.replace(character, "")

        return string

    clean_product_name: callable = lambda string: remove_characters(string.split(" - ")[1], "[", "]").split("/")

    releases: dict = {}
    year_groups: list = _group_list_by_element_attributes(text_area, _symbol_count_equals("=", 6))

    for year_group in year_groups:
        year: str = remove_characters(year_group[0], "=", " ")
        month_groups = _group_list_by_element_attributes(year_group[1:], _symbol_count_equals("=", 8))

        for month_group in month_groups:
            month: str = remove_characters(month_group[0], "=", " ")
            products: map = map(clean_product_name, month_group[1:])

            for day in products:
                for product in day:
                    releases[product] = f"{year}/{month_number[month]:02}"

    return releases


def _get_month_name_to_number_dict() -> dict:
    return {month: index for index, month in enumerate(calendar.month_name) if month}


def _group_list_by_element_attributes(flat_list: list, function: callable) -> list:
    g = (list(x) for _, x in groupby(flat_list, key=function))
    return [a + b for a, b in zip(g, g)]


def _symbol_count_equals(symbol: str, count: int) -> callable:
    return lambda string: string.count(symbol) == count


class ResponseStatusError(Exception):
    def __init__(self, status_code: int):
        super().__init__(f"YGOPRODECK API returned status code {status_code}")

import os
