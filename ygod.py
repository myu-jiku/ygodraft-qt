from PySide6.QtWidgets import (QApplication)

from backend import card_images
from backend import collection
from backend import database

from frontend.abstract_menu import AbstractMenu
from frontend.draft_options_window import DraftOptionsWindow
from frontend.window_manager import WindowManager


if __name__ == "__main__":
    collection.ensure_directory()

    import sys

    app = QApplication()

    class MainMenu(AbstractMenu):
        def init_buttons(self):
            self.add_button("Draft", lambda: self.parent().open_window(DraftOptionsWindow()))
            self.add_button("Update", database.update)
            self.add_button("Download Images", card_images.download_missing)

    window_manager = WindowManager(MainMenu)

    window_manager.show()
    app.exec()

