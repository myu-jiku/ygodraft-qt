
from PySide6.QtCore import (QEvent, Qt, Signal)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QMenu)

from backend import collection

from frontend.collection_list import CollectionList
from frontend.popup_dialog import PopupDialog


class EditCollectionsMenu(QWidget):
    collections_changed = Signal()

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
        self.main_layout = QVBoxLayout(self)

        self.collection_list = CollectionList()
        self.collection_list.installEventFilter(self)

        self.main_layout.addWidget(self.collection_list)

    def edit_collection(self) -> None:
        pass

    def rename_collection(self) -> None:
        collection_name = self.collection_list.currentItem().text()

        popup = PopupDialog(f"Enter new name for collection '{collection_name}'", True)
        
        popup.buttons.accepted.connect(lambda: collection.copy(
            collection_name,
            popup.line_edit.text(),
            True
        ))

        popup.exec()

        self.collections_changed.emit()

    def copy_collection(self) -> None:
        pass

    def export_collection(self) -> None:
        collection_name = self.collection_list.currentItem().text()

        try:
            collection.export_as_banlist(collection_name)
        except FileExistsError:
            popup = PopupDialog(f"Replace file with name '{collection_name}.conf'?")
            popup.buttons.accepted.connect(lambda: collection.export_as_banlist(collection_name, overwrite_file=True))
            popup.exec()

    def delete_collection(self) -> None:
        pass

    def eventFilter(self, source, event) -> None:
        if event.type() == QEvent.ContextMenu and source is self.collection_list and self.collection_list.currentRow() != -1:
            menu = QMenu()
            for action in self.actions:
                menu.addAction(action)

            executed_action = menu.exec(event.globalPos())
            
            if executed_action:
                print(executed_action.text())
                print(self.collection_list.currentItem().text())
                self.actions[executed_action.text()]()

            return True

        return super().eventFilter(source, event)

