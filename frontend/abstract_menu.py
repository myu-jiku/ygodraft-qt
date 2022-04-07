from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QSizePolicy)

from frontend.window_manager import WindowManager


class AbstractMenu(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup()
        self.init_buttons()

    def setup(self) -> None:
        self.root_layout = QVBoxLayout(self)

        self.root_layout.addWidget(QWidget())
        self.root_layout.addWidget(QWidget())

        self.buttons: int = 0

    def init_buttons(self) -> None:
        pass

    def add_button(self, text: str, function: callable = None) -> None:
        button = QPushButton(text=text)
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        button.setMaximumSize(16777215, 100)
        button.clicked.connect(function)

        self.buttons += 1
        self.root_layout.insertWidget(self.buttons, button)

