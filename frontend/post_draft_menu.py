from collections import Counter

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton)

from backend import collection

from frontend.edit_collections_menu import EditCollectionsMenu
from frontend.popup_dialog import PopupDialog


class PostDraftMenu(QWidget):
    def __init__(self, draft: Counter) -> None:
        super().__init__()

        self.draft: list = draft

        self.main_layout = QVBoxLayout(self)

        self.view_draft_button = QPushButton(text="View Draft")

        self.collections_menu = EditCollectionsMenu()
        self.collections_menu.collection_list.currentItemChanged.connect(self.check_item_selected)
        self.collections_menu.update_list = lambda: EditCollectionsMenu.update_list(self.collections_menu) or self.collections_menu.collection_list.currentItemChanged.connect(self.check_item_selected)
        
        self.add_to_collection_button = QPushButton(text="Add Draft To Collection")
        self.add_to_collection_button.setEnabled(False)
        self.add_to_collection_button.clicked.connect(self.add_to_collection)

        self.main_layout.addWidget(self.view_draft_button)
        self.main_layout.addWidget(self.collections_menu)
        self.main_layout.addWidget(self.add_to_collection_button)

    def add_to_collection(self) -> None:
        def close_window():
            parent = self.parent()
            parent.close_all_windows()
            parent.open_window(EditCollectionsMenu())

        collection_name: str = self.collections_menu.collection_list.currentItem().text()
        popup = PopupDialog(f"Add draft to collection '{collection_name}'?")
        popup.buttons.accepted.connect(lambda: print("hi"))
        popup.buttons.accepted.connect(lambda: collection.add_cards(collection_name, self.draft))
        popup.buttons.accepted.connect(close_window)
        popup.exec()

    def check_item_selected(self) -> None:
        if self.collections_menu.collection_list.currentItem():
            self.add_to_collection_button.setEnabled(True)
        else:
            self.add_to_collection_button.setEnabled(False)

