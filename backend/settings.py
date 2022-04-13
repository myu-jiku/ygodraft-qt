import json

from backend import paths


def get(option: str) -> object:
    return access_settings().get(option)


def set(option: str, value: object) -> None:
    settings: dict = access_settings()

    settings[option] = value
    write(settings)


# ensures that file exists and defaults are applied
def access_settings() -> dict:
    ensure_file()

    settings: dict = read()
    settings = insert_into_defaults(settings)

    return settings


# combines settings in file with default values
def insert_into_defaults(settings: dict) -> dict:
    defaults = {
        # draft settings
        "draft_rounds": 20,
        "card_bundles": 3,
        "cards_per_bundle": 3,
        "duplicates_in_pool": 3,
    }

    # anything set in settings overwrites defaults
    return {**defaults, **settings}


def ensure_file() -> None:
    if not paths.settings_path.is_file():
        write({})


def read() -> dict:
    with open(paths.settings_path, "r") as file:
        data = file.read()

    return json.loads(data)


def write(settings: dict) -> None:
    data = json.dumps(settings)

    with open(paths.settings_path, "w") as file:
        file.write(data)
