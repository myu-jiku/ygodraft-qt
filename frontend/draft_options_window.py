

from PySide6.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QSizePolicy, QLabel, QFrame, QSpinBox, QPushButton)

from backend import settings

from frontend.round_draft_window import RoundDraftWindow
from frontend.set_selection_window import SetSelectionWindow


class OptionBox(QWidget):
    def __init__(self, text: str, max_value: int, min_value: int = 1) -> None:
        self.label_text: str = text
        self.max_value: int = max_value
        self.min_value: int = min_value

        super().__init__()
        self.setup_ui()

    def setup_ui(self) -> None:
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.main_layout = QHBoxLayout(self)

        self.text_label = QLabel(text=self.label_text)
        self.text_label.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.main_layout.addWidget(self.text_label)

        self.spin_box = QSpinBox()
        self.spin_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
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
        self.selected_sets = []

    def setup_ui(self) -> None:
        self.grid = QGridLayout(self)
        
        defaults: dict = settings.access_settings()

        self.draft_rounds_box = OptionBox("Draft Rounds", 300)
        self.draft_rounds_box.setValue(defaults["draft_rounds"])

        self.card_bundles_box = OptionBox("Card Bundles/Choices", 50)
        self.card_bundles_box.setValue(defaults["card_bundles"])

        self.cards_per_bundle_box = OptionBox("Cards per Bundle", 50)
        self.cards_per_bundle_box.setValue(defaults["cards_per_bundle"])

        self.duplicates_box = OptionBox("Duplicates in Card Pool", 10)
        self.duplicates_box.setValue(defaults["duplicates_in_pool"])

        self.select_sets_button = QPushButton(text="Select Sets")
        self.select_sets_button.clicked.connect(self.set_selection)

        self.view_contents_button = QPushButton(text="View Contents")
        

        self.start_draft_button = QPushButton(text="Start Draft")
        self.start_draft_button.clicked.connect(self.start_draft)
        self.start_draft_button.setEnabled(False)

        self.grid.addWidget(self.draft_rounds_box, 0, 0)
        self.grid.addWidget(self.card_bundles_box, 0, 1)
        self.grid.addWidget(self.duplicates_box, 1, 0)
        self.grid.addWidget(self.cards_per_bundle_box, 1, 1)
        self.grid.addWidget(self.select_sets_button, 2, 0)
        self.grid.addWidget(self.view_contents_button, 2, 1)
        self.grid.addWidget(self.start_draft_button, 3, 0, 1, 2)

    def set_selection(self) -> None:
        parent = self.parent()

        def change_selected_sets():
            self.selected_sets = parent.get_current_widget().get_selected_sets()
            
            if self.selected_sets:
                self.start_draft_button.setEnabled(True)
            else:
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
            self.selected_sets
        ))
