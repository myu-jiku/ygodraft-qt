
from PySide6.QtCore import (QEvent, Qt, Signal, QSize)
from PySide6.QtGui import (QIcon)
from PySide6.QtWidgets import (QWidget, QGridLayout, QMenu, QToolButton, QLineEdit)

from backend import collection

from frontend.collection_list import CollectionList
from frontend.popup_dialog import PopupDialog


class EditCollectionsMenu(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_vars()
        self.init_ui()

    def init_vars(self) -> None:
        self.actions = {
            "Edit": self.edit_collection,
            "Rename": self.rename_collection,
            "Copy": self.copy_collection,
            "Export": self.export_collection,
            "Delete": self.delete_collection
        }

    def init_ui(self) -> None:
        self.main_layout = QGridLayout(self)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Collections")
        self.search_bar.editingFinished.connect(self.update_list)

        self.add_collection_button = QToolButton()
        plus_icon = QIcon()
        plus_icon.addFile("images/ui/plus_icon.svgz", QSize(), QIcon.Normal, QIcon.Off)
        self.add_collection_button.setIcon(plus_icon)
        self.add_collection_button.clicked.connect(self.new_collection)

        self.collection_list = CollectionList()
        self.collection_list.installEventFilter(self)

        self.main_layout.addWidget(self.search_bar, 0, 0)
        self.main_layout.addWidget(self.add_collection_button, 0, 1)
        self.main_layout.addWidget(self.collection_list, 1, 0, 1, 2)

    def new_collection(self) -> None:
        popup = PopupDialog(f"Enter name for new collection", True)
        popup.buttons.accepted.connect(lambda: collection.new(popup.line_edit.text()))
        popup.exec()
        self.update_list()

    def edit_collection(self) -> None:
        pass

    def rename_collection(self) -> None:
        self.copy_collection(True)

    def copy_collection(self, rename: bool = False) -> None:
        collection_name = self.collection_list.currentItem().text()

        popup = PopupDialog(f"Enter new name for{' copy of' * (1 - rename)} collection '{collection_name}'", True)

        popup.buttons.accepted.connect(lambda: collection.copy(
            collection_name,
            popup.line_edit.text(),
            rename
        ))

        popup.exec()
        self.update_list()

    def export_collection(self) -> None:
        collection_name = self.collection_list.currentItem().text()

        try:
            collection.export_as_banlist(collection_name)
        except FileExistsError:
            popup = PopupDialog(f"Replace file with name '{collection_name}.conf'?")
            popup.buttons.accepted.connect(lambda: collection.export_as_banlist(collection_name, overwrite_file=True))
            popup.exec()

    def delete_collection(self) -> None:
        collection_name = self.collection_list.currentItem().text()

        popup = PopupDialog(f"Do you want to delete the collection '{collection_name}'?")
        popup.buttons.accepted.connect(lambda: collection.delete(collection_name))
        popup.exec()
        self.update_list()

    def update_list(self) -> None:
        self.collection_list.setParent(QWidget())
        self.collection_list = CollectionList(self.search_bar.text())
        self.collection_list.installEventFilter(self)

        self.main_layout.addWidget(self.collection_list, 1, 0, 1, 2)

    def eventFilter(self, source, event) -> None:
        if event.type() == QEvent.ContextMenu and source is self.collection_list and self.collection_list.currentRow() != -1:
            menu = QMenu()
            for action in self.actions:
                menu.addAction(action)

            executed_action = menu.exec(event.globalPos())
            
            if executed_action:
                self.actions[executed_action.text()]()

            return True

        return super().eventFilter(source, event)

