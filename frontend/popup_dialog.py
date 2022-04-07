from PySide6.QtCore import (Qt)
from PySide6.QtWidgets import (QDialog, QLabel, QVBoxLayout, QDialogButtonBox, QLineEdit)


class PopupDialog(QDialog):
    def __init__(self, text: str, add_line_edit: bool = False) -> None:
        super().__init__()

        self.main_layout = QVBoxLayout(self)
        self.line_edit = QLineEdit()
        self.buttons = QDialogButtonBox()

        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.close)
        self.buttons.rejected.connect(self.close)

        self.main_layout.addWidget(QLabel(text=text))

        if add_line_edit:
            self.main_layout.addWidget(self.line_edit)

        self.main_layout.addWidget(self.buttons)

