from PySide6.QtWidgets import (QListWidget)

from backend import collection


class CollectionList(QListWidget):
    def __init__(self, search_filter: str = "") -> None:
        super().__init__()

        items = collection.search(search_filter)
        items.sort()
        self.addItems(items)

