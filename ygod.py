from PySide6.QtCore import (QSize, Qt)
from PySide6.QtGui import (QAction, QIcon)
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar)

from backend import card_images
from backend import collection
from backend import database

from frontend.abstract_menu import AbstractMenu
from frontend.draft_options_window import DraftOptionsWindow
from frontend.edit_collections_menu import EditCollectionsMenu
from frontend.window_manager import WindowManager


if __name__ == "__main__":
    collection.ensure_directory()

    import sys

    app = QApplication()

    class MainMenu(AbstractMenu):
        def init_buttons(self):
            self.add_button("Draft", lambda: self.parent().open_window(DraftOptionsWindow()))
            self.add_button("Collections", lambda: self.parent().open_window(EditCollectionsMenu()))
            self.add_button("Update", database.update)
            self.add_button("Download All Images", card_images.download_all)

    window_manager = WindowManager(MainMenu)

    main_window = QMainWindow()
    main_window.setCentralWidget(window_manager)
    main_window.resize(800, 600)

    tool_bar = QToolBar()
    tool_bar.setMovable(False)
    tool_bar.setContextMenuPolicy(Qt.PreventContextMenu)

    go_back_action = QAction()
    back_icon = QIcon()
    back_icon.addFile("images/ui/arrow_back.svgz", QSize(), QIcon.Normal, QIcon.Off)
    go_back_action.setIcon(back_icon)
    go_back_action.triggered.connect(lambda: window_manager.go_back())
    tool_bar.addAction(go_back_action)

    main_window.addToolBar(tool_bar)

    main_window.show()
    app.exec()

