from PySide6.QtCore import (Qt, Signal, QMargins)
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QToolButton, QVBoxLayout, QHBoxLayout, QScrollArea, QSizePolicy)

from backend import database

from frontend.card_set_button import CardSetButton


class SetSelectionWindow(QWidget):
    deselect_all: bool = False
    sort_reversed: bool = False
    card_set_widgets: list = None
    selected_sets: list = None
    filtered_sets_quantity: int = 0
    finished = Signal()

    def __init__(self, selected_sets: list = None) -> None:
        self.db_sets: list = database.get_sets()

        self.card_set_widgets = self.card_set_widgets or []
        self.selected_sets = selected_sets or []

        super().__init__()
        self.init_gui()
        self.generate_sets()

    def init_gui(self) -> None:
        self.main_layout = QVBoxLayout(self)

        self.search_results_label = QLabel()
        self.select_all_button = QPushButton()
        self.confirm_button = QPushButton()
        
        self.text_input = QLineEdit()
        self.set_type_menu = QComboBox()
        self.sort_menu = QComboBox()
        self.reverse_sort_button = QToolButton()
        self.text_input_holder = QWidget()
        self.text_input_holder_layout = QHBoxLayout(self.text_input_holder)
        self.text_input_holder_layout.addWidget(self.text_input)
        self.text_input_holder_layout.addWidget(self.set_type_menu)
        self.text_input_holder_layout.addWidget(self.sort_menu)
        self.text_input_holder_layout.addWidget(self.reverse_sort_button)
        self.text_input_holder_layout.setContentsMargins(QMargins())

        self.column_descriptions = QWidget()
        self.column_descriptions_layout = QHBoxLayout(self.column_descriptions)

        self.scroll_area = QScrollArea()
        self.scroll_holder = QWidget()
        self.scroll_holder_layout = QVBoxLayout(self.scroll_holder)
        self.scroll_holder_layout.addWidget(self.scroll_area)
        self.scroll_holder_layout.setContentsMargins(QMargins())

        self.main_layout.addWidget(self.text_input_holder)
        self.main_layout.addWidget(self.search_results_label)
        self.main_layout.addWidget(self.select_all_button)
        self.main_layout.addWidget(self.column_descriptions)
        self.main_layout.addWidget(self.scroll_holder)
        self.main_layout.addWidget(self.confirm_button)

        self.text_input.editingFinished.connect(self.generate_sets)
        self.text_input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.set_type_menu.setPlaceholderText("Product type")
        self.set_type_menu.addItems(["All"] + database.get_set_types(self.db_sets))
        self.set_type_menu.currentTextChanged.connect(self.generate_sets)

        self.sort_menu.setPlaceholderText("Sort")
        self.sort_menu.addItems(["Name", "Date", "Type"])
        self.sort_menu.currentTextChanged.connect(self.generate_sets)
        
        self.reverse_sort_button.setArrowType(Qt.UpArrow)
        self.reverse_sort_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.reverse_sort_button.clicked.connect(self.change_sort_direction)

        self.select_all_button.setText("Select all")
        self.select_all_button.clicked.connect(self.select_all)
        self.select_all_button.setCheckable(True)

        self.column_descriptions_layout.addWidget(QLabel(text=f"{3 * ' '}Product Name"))
        self.column_descriptions_layout.addWidget(QLabel(text=f"Release Date{5 * ' '}", alignment=Qt.AlignCenter))
        self.column_descriptions_layout.addWidget(QLabel(text=f"Category{15 * ' '}", alignment=Qt.AlignCenter))

        self.confirm_button.setText("Confirm")
        self.confirm_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.confirm_button.setMaximumSize(16777215, 50)
        self.confirm_button.setMinimumSize(0, 50)
        self.confirm_button.clicked.connect(self.finished.emit)

    def flush_scroll_area(self) -> None:
        self.scroll_holder_layout.removeWidget(self.scroll_area)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)

        self.scroll_holder_layout.addWidget(self.scroll_area)

    def count_selected_sets(self, card_sets: list = None) -> None:
        self.selected_sets = list(
            set(self.selected_sets) \
            - {widget.labels["name"].text() for widget in self.card_set_widgets} \
            | {widget.labels["name"].text() for widget in self.card_set_widgets if widget.selected}
        )

    def update_results_label(self) -> None:
        self.count_selected_sets()
        self.search_results_label.setText(f"{self.filtered_sets_quantity} results / {len(self.selected_sets)} selected")

    def change_sort_direction(self) -> None:
        self.sort_reversed = not self.sort_reversed
        self.reverse_sort_button.setArrowType([Qt.UpArrow, Qt.DownArrow][self.sort_reversed])
        self.generate_sets()

    def generate_sets(self) -> None:
        self.count_selected_sets()
        self.flush_scroll_area()

        self.deselect_all = False
        self.select_all_button.setChecked(False)

        card_sets = list(database.filter_sets_and_return_attributes(self.text_input.text(), self.db_sets))
        card_sets.sort(key=lambda card_set: card_set[self.sort_menu.currentText().lower() or "date"] or "ZZZZ", reverse=self.sort_reversed)

        if not self.set_type_menu.currentText() in ["", "All"]:
            set_type = self.set_type_menu.currentText()
            card_sets = list(filter(lambda a: a["type"] == set_type, card_sets))

        self.filtered_sets_quantity = len(card_sets)
        self.update_results_label()

        self.card_set_widgets = []

        for card_set in card_sets:
            widget = CardSetButton(card_set)

            if card_set["name"] in self.selected_sets:
                widget.selected = True
                widget.update_frame_style()

            widget.switched.connect(self.update_results_label)

            self.scroll_content_layout.addWidget(widget)
            self.card_set_widgets.append(widget)

        self.scroll_content_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)

    def select_all(self) -> None:
        select_all: bool = not self.deselect_all

        for widget in self.card_set_widgets:
            widget.selected = select_all
            widget.update_frame_style()

        self.deselect_all = select_all
        self.update_results_label()

    def get_selected_sets(self) -> list:
        selected_sets: list = []

        for widget in self.card_set_widgets:
            if widget.selected:
                selected_sets.append(widget.labels["name"].text())

        return selected_sets
