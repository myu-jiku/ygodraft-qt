import os
import requests
from glob import glob
from random import choice

from backend import database


image_type: list = ["big"]

images: dict = {
    "small": {"path": "images/small/", "url": "https://storage.googleapis.com/ygoprodeck.com/pics_small/"},
    "big": {"path": "images/big/", "url": "https://storage.googleapis.com/ygoprodeck.com/pics/"},
    "cropped": {"path": "images/cropped/", "url": "https://storage.googleapis.com/ygoprodeck.com/pics_artgame/"}
}

placeholders: list = [
    67284108,  # black sheep token
    56597273,  # cloudian token
    46173680,  # doomsday token 1
    46173681,  # doomsday token 2
    35268888,  # ghost token
    93912846,  # gift fiend token
    60764582,  # lamb token 1
    60764583,  # lamb token 2
    47658965,  # laval token
    42671152,  # malus token
    24874631,  # metal fiend token
    17418745,  # photon token
    82324106,  # soul token
     9047461,  # steam token
]


def get_image_or_placeholder(card_id: int) -> str:
    path: str = get_image_path(card_id)
    if os.path.isfile(path):
        return path
    else:
        return placeholder_from_string(f"{card_id}")


def random_placeholder() -> str:
    return get_image_path(choice(placeholders))


def random_cropped_image(download_new: bool = True) -> str:
    image_type.append("cropped")
    card_ids: list = list(database.get_cards("id"))
    card_id: int = choice(card_ids)

    ensure_directory()

    if download_new and download_card(card_id):
        path: str = get_image_path(card_id)
    else:
        path: str = choice(glob(f"{images[get_image_type()]['path']}/*.jpg") or [""])

    image_type.pop(-1)
    return path


def placeholder_from_string(name: str):
    placeholder: int = placeholders[sum([ord(c) for c in name]) % len(placeholders)]
    return get_image_path(placeholder)


def download_all() -> None:
    download_placeholders()
    download_missing(database.get_cards("id"))


def download_placeholders() -> None:
    download_missing(placeholders)


def download_missing(cards: list, retries: int = 0, cache: list = None) -> list:
    number_of_cards: int = len(cards)
    cards_missed: bool = False

    ensure_directory()

    cache_given: bool = cache is not None
    new_cache: list = []

    for index, card in enumerate(cards):
        if cache_given and card in cache:
            continue

        print(f"{index + 1}/{number_of_cards}")
        download_successful = download_card(card)

        if download_successful and cache_given:
            new_cache.append(card)
        elif not cards_missed:
            cards_missed = True

    if cards_missed and retries:
        get_missing_card_images(retries - 1)

    if cache_given:
        return cache + new_cache


def download_card(card_id: int, offset: int = 0) -> bool:
    path: str = get_image_path(card_id)

    if not os.path.isfile(path):
        url: str = f"{images[get_image_type()]['url']}{card_id + offset}.jpg"
        response = requests.get(url)

        if response.status_code != 200:
            print(response.status_code, url)

            if offset:
                return False

            return download_card(card_id, 1) or download_card(card_id, -1)

        with open(path, "wb") as file:
            file.write(response.content)

    return True


def ensure_directory() -> None:
    path: str = images[get_image_type()]["path"]
    if not os.path.exists(path):
        os.makedirs(path)


def get_image_path(card_id: int) -> str:
    return f"{images[get_image_type()]['path']}{card_id}.jpg"


def get_image_type() -> str:
    return image_type[-1]

