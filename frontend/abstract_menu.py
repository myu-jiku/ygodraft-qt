
from PySide6 import QtWidgets

from frontend.window_manager import WindowManager


class AbstractMenu(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup()
        self.init_buttons()

    def setup(self) -> None:
        self.root_layout = QtWidgets.QVBoxLayout(self)

    def init_buttons(self) -> None:
        pass

    def add_button(self, text: str, function: callable = None) -> None:
        button = QtWidgets.QPushButton(text=text)
        button.clicked.connect(function)
        self.root_layout.addWidget(button)

