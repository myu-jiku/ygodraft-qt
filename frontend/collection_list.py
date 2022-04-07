from PySide6.QtWidgets import (QListWidget)

from backend import collection


class CollectionList(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_items()

    def init_items(self) -> None:
        self.addItems(collection.get_collections())

