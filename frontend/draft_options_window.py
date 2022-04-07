from copy import copy

from PySide6.QtCore import (QSize)
from PySide6.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QSizePolicy, QLabel, QFrame, QSpinBox, QPushButton)

from backend import database
from backend import settings

from frontend.round_draft_window import RoundDraftWindow
from frontend.set_selection_window import SetSelectionWindow


class OptionBox(QFrame):
    def __init__(self, text: str, max_value: int, min_value: int = 1) -> None:
        self.label_text: str = text
        self.max_value: int = max_value
        self.min_value: int = min_value

        super().__init__()
        self.setup_ui()

    def setup_ui(self) -> None:
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.main_layout = QHBoxLayout(self)

        self.text_label = QLabel(text=self.label_text)
        self.text_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.main_layout.addWidget(self.text_label)

        self.spin_box = QSpinBox()
        self.spin_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.spin_box.setMaximum(self.max_value)
        self.spin_box.setMinimum(self.min_value)
        self.spin_box.setMinimumSize(55, 0)
        self.main_layout.addWidget(self.spin_box)
    
    def setValue(self, value: int) -> None:
        self.spin_box.setValue(value)
    
    def value(self) -> int:
        return self.spin_box.value()


class DraftOptionsWindow(QWidget):
    def __init__(self, selected_sets: list = None) -> None:
        self.selected_sets: list = selected_sets or []

        super().__init__()
        self.init_vars()
        self.setup_ui()

    def init_vars(self) -> None:
        self.cards_in_sets: list = []
        self.layout_position: int = 0

    def setup_ui(self) -> None:
        self.grid = QGridLayout(self)
        
        defaults: dict = settings.access_settings()

        self.draft_rounds_box = OptionBox("Draft Rounds", 300)
        self.draft_rounds_box.setValue(defaults["draft_rounds"])
        self.set_size(self.draft_rounds_box)

        self.card_bundles_box = OptionBox("Card Bundles/Choices", 50)
        self.card_bundles_box.setValue(defaults["card_bundles"])
        self.set_size(self.card_bundles_box)

        self.cards_per_bundle_box = OptionBox("Cards per Bundle", 50)
        self.cards_per_bundle_box.setValue(defaults["cards_per_bundle"])
        self.set_size(self.cards_per_bundle_box)

        self.duplicates_box = OptionBox("Duplicates in Card Pool", 10)
        self.duplicates_box.setValue(defaults["duplicates_in_pool"])
        self.set_size(self.duplicates_box)

        self.select_sets_button = QPushButton(text="Select Sets")
        self.set_size(self.select_sets_button)
        self.select_sets_button.clicked.connect(self.set_selection)

        self.view_contents_button = QPushButton(text="View Contents")
        self.set_size(self.view_contents_button)

        self.start_draft_button = QPushButton(text="Start Draft")
        self.set_size(self.start_draft_button)
        self.start_draft_button.clicked.connect(self.start_draft)
        self.start_draft_button.setEnabled(False)

        self.add_to_layout(QWidget())
        self.add_to_layout(self.draft_rounds_box, self.card_bundles_box)
        self.add_to_layout(self.duplicates_box, self.cards_per_bundle_box)
        self.add_to_layout(QWidget())
        self.add_to_layout(self.select_sets_button, self.view_contents_button)
        self.add_to_layout(self.start_draft_button)
        self.add_to_layout(QWidget())

    def set_size(self, widget: QWidget) -> None:
        widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        widget.setMaximumSize(QSize(16777215, 80))

    def add_to_layout(self, widget1: QWidget, widget2: QWidget = None) -> None:
        if widget2:
            self.grid.addWidget(widget1, self.layout_position, 0)
            self.grid.addWidget(widget2, self.layout_position, 1)
        else:
            self.grid.addWidget(widget1, self.layout_position, 0, 1, 2)

        self.layout_position += 1

    def set_selection(self) -> None:
        parent = self.parent()

        def change_selected_sets():
            selected_sets = copy(self.selected_sets)
            self.selected_sets = parent.get_current_widget().get_selected_sets()
            
            if self.selected_sets and self.selected_sets != selected_sets:
                self.start_draft_button.setEnabled(True)
                self.cards_in_sets = database.get_cards_from_sets(self.selected_sets)
            elif not self.selected_sets:
                self.start_draft_button.setEnabled(False)

            parent.go_back()

        parent.open_window(SetSelectionWindow(self.selected_sets))
        parent.get_current_widget().finished.connect(change_selected_sets)

    def start_draft(self) -> None:
        self.parent().open_window(RoundDraftWindow(
            self.draft_rounds_box.value(),
            self.card_bundles_box.value(),
            self.cards_per_bundle_box.value(),
            self.duplicates_box.value(),
            self.cards_in_sets
        ))
