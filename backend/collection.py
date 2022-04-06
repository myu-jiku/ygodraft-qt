import os
import json

from backend import database
from collections import Counter
from glob import glob


directory: str = "collections/"
version: int = 1


def get_cards(name: str) -> dict:
    return read(name)["cards"]


def add_card(name: str, card: str) -> None:
    add_cards(name, [{"id": database.get_card_id(card)}])


def remove_card(name: str, card: str) -> None:
    add_cards(name, [{"id": database.get_card_id(card)}], subtract=True)


def change_banlist(name: str, card: str, limit: int) -> None:
    collection: dict = read(name)
    
    collection["limits"][str(database.get_card_id(card))] = limit
    collection["limits"] = {k: v for k, v in collection["limits"].items() if v < 3 and v >= 0}

    write(name, collection)


def add_cards(name: str, cards: list, subtract: bool = False) -> None:
    collection: dict = read(name)
    cards_old: Counter = Counter(collection["cards"])
    #cards_new: Counter = Counter(map(lambda card: str(card["id"]), cards))
    cards_new = Counter({str(k): v for k, v in dict(cards).items()})

    add_or_subtract_from_collection: callable = cards_old.__sub__ if subtract else cards_old.__add__

    collection["cards"] = add_or_subtract_from_collection(cards_new)

    write(name, collection)


def export_as_banlist(name: str, path: str = "", target_name: str = None, overwrite_file: bool = False) -> None:
    target_name = target_name or name
    
    slash: chr = '/' * (bool(path) and bool(("  " + path)[-2] != '/'))
    full_path: str = f"{path}{slash}{target_name}.conf"
    print(slash)

    if os.path.isfile(full_path) and not overwrite_file:
        raise FileExistsError(f"File with name \"{name}\" already exists")

    lines = [f"!{name}\n$whitelist\n", *_format_as_lflist(name)]

    with open(full_path, "w") as file:
        file.writelines(lines)


def copy(source: str, target: str, rename: bool = False) -> None:
    if not source in get_collections():
        raise FileNotFoundError(f"Could not find collection with name \"{source}\"")

    new(target)

    write(target, read(source))

    if rename:
        delete(source)


# returns name if the creation was successful
def new(name: str) -> str:
    if not name:
        raise EmptyCollectionNameError
    elif name in get_collections():
        raise FileExistsError(f"Collection with name \"{name}\" already exists")
    else:
        try:
            write(name, template())
        except Exception:
            raise CouldNotCreateFileError(name)

    return name


def delete(name: str) -> None:
    os.remove(get_path(name))


def ensure_directory() -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def read(name: str) -> dict:
    with open(get_path(name), "r") as file:
        collection = file.read()

    return json.loads(collection)


def write(name: str, collection: dict) -> None:
    json_string = json.dumps(collection)

    with open(get_path(name), "w") as file:
        file.write(json_string)


def template() -> dict:
    return {
        "version": version,
        "cards": {},
        "limits": {},
        "wildcards": 0,
        "wins": 0,
        "losses": 0
    }


def get_path(name: str) -> str:
    return directory + name


def get_collections() -> list:
    return glob("*", root_dir=directory)


def _format_as_lflist(name: str) -> list:
    collection = read(name)

    def _format(card_id):
        card_quantity = min(
            collection["cards"][card_id],
            collection["limits"].get(card_id, 3)
        )

        return f"{card_id} {card_quantity}\n"

    return list(map(_format, collection["cards"].keys()))


class EmptyCollectionNameError(Exception):
    def __init__(self):
        super().__init__("Collection name empty")


class CouldNotCreateFileError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Could not create file with name \"{name}\"")

