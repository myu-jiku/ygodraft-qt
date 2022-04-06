from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton)

from frontend.window_manager import WindowManager


class AbstractMenu(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup()
        self.init_buttons()

    def setup(self) -> None:
        self.root_layout = QVBoxLayout(self)

    def init_buttons(self) -> None:
        pass

    def add_button(self, text: str, function: callable = None) -> None:
        button = QPushButton(text=text)
        button.clicked.connect(function)
        self.root_layout.addWidget(button)

