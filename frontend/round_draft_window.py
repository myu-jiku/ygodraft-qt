from collections import Counter
from copy import copy

from PySide6.QtCore import (Qt, Signal)
from PySide6.QtGui import (QCursor)
from PySide6.QtWidgets import (QWidget, QVBoxLayout)

from backend import collection
from backend import draft

from frontend import draft_ui


class RoundDraftWindow(QWidget):
    rounds: int
    card_bundles: int
    cards_per_bundle: int
    duplicates_in_pool: int
    card_pool: list
    selected_cards: Counter
    draft_finished = Signal()

    def __init__(
        self,
        rounds: int,
        card_bundles: int,
        cards_per_bundle: int,
        duplicates_in_pool: int,
        card_pool: list
    ) -> None:
        self.rounds = rounds
        self.card_bundles = card_bundles
        self.cards_per_bundle = cards_per_bundle
        self.duplicates_in_pool = duplicates_in_pool
        self.card_pool = copy(card_pool)

        super().__init__()
        self.setup()
        self.create_draft_window()

    def setup(self) -> None:
        self.download_cache: list = []

        self.main_layout = QVBoxLayout(self)
        self.draft_window = draft_ui.DraftSubWindow(self.download_cache)

        self.round_counter: int = 1
        self.card_pool = self.card_pool * self.duplicates_in_pool
        self.selected_cards = Counter()
        self.choices = []

    def create_draft_window(self) -> None:
        self.choices, self.card_pool = draft.generate_bundles_and_get_new_pool(self.card_pool, self.card_bundles, self.cards_per_bundle)
        
        self.draft_window.draft_tab.generate_choices(self.choices)
        self.draft_window.draft_tab.confirm_button.clicked.connect(self.next_round)
        self.draft_window.currentChanged.connect(self.refresh_selected_cards_tab)
        self.main_layout.addWidget(self.draft_window)

    def next_round(self) -> None:
        self.round_counter += 1
        choice = self.choices[self.draft_window.draft_tab.choices_tool_box.currentIndex()]
        self.selected_cards = self.selected_cards + Counter(choice)

        if self.round_counter > self.rounds:
            self.draft_finished.emit()
            try:
                collection.new("default")
            except FileExistsError:
                pass
            collection.add_cards("default", self.selected_cards)
            collection.export_as_banlist("default", overwrite_file=True)
            self.parent().go_back()
        else:
            self.download_cache = self.draft_window.draft_tab.download_cache
            tmp: set = set(self.card_pool)
            self.download_cache = [card for card in self.download_cache if card in tmp][-50:]
            print(self.download_cache)
            self.draft_window.deleteLater()
            self.draft_window = draft_ui.DraftSubWindow(self.download_cache)
            self.create_draft_window()

    def refresh_selected_cards_tab(self) -> None:
        if not self.draft_window.selected_cards_tab.selected_cards_generated \
        and self.draft_window.currentIndex() == 1:
            self.setCursor(QCursor(Qt.WaitCursor))
            self.draft_window.selected_cards_tab.generate_selected_cards(self.selected_cards)
            self.setCursor(QCursor(Qt.ArrowCursor))

