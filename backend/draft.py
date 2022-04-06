from backend import settings
from random import shuffle


def generate_bundles_and_get_new_pool(
    card_pool: list,
    card_bundles: int = settings.get("card_bundles"),
    cards_per_bundle: int = settings.get("cards_per_bundle")
) -> (list, list):
    shuffle(card_pool)

    bundles: list = []
    for _ in range(card_bundles):
        bundles.append(card_pool[:cards_per_bundle])
        card_pool = card_pool[cards_per_bundle:]

    return bundles, card_pool

