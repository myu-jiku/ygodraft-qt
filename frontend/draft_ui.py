import webbrowser
from collections import Counter

from PySide6.QtCore import (Qt, QSize)
from PySide6.QtGui import (QCursor, QIcon, QPixmap)
from PySide6.QtWidgets import (QWidget, QToolBox, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QTabWidget)

from backend import card_images
from backend import database
from backend import draft


generic_wiki_url: str = "https://yugipedia.com/wiki/"


class DraftTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup()

    def setup(self) -> None:
        self.choices_tool_box = QToolBox()
        self.confirm_button = QPushButton(text="Confirm")

        self.main_layout = QVBoxLayout(self)

        self.main_layout.addWidget(self.choices_tool_box)
        self.main_layout.addWidget(self.confirm_button)

    def generate_choices(self, choices: list) -> None:
        for index, choice in enumerate(choices):
            page = QWidget()
            page_layout = QHBoxLayout(page)

            for card_id in choice:
                page_layout.addWidget(self.make_card(card_id))

            self.choices_tool_box.addItem(page, f"Choice {index + 1}")

    def make_card(self, card_id: int) -> QPushButton:
        card = QPushButton()
        card.setFocusPolicy(Qt.NoFocus)

        card.setIconSize(QSize(168, 246))
        card.setMaximumSize(QSize(176, 254))

        card.setCursor(QCursor(Qt.PointingHandCursor))

        image = QIcon()
        image.addPixmap(
            QPixmap(f"{card_images.get_image_or_placeholder(card_id)}"),
            QIcon.Normal,
            QIcon.Off
        )

        card.setIcon(image)

        card_name = database.get_cards()[f"{card_id}"]["name"]
        card.clicked.connect(lambda: webbrowser.open(f"{generic_wiki_url}{card_name.replace('#', ' ')}"))
        card.setToolTip(f"{card_name} (view on Yugipedia)")

        return card


class SelectedCardsTab(QWidget):
    selected_cards_generated: bool = False

    def __init__(self) -> None:
        super().__init__()
        self.setup()

    def setup(self) -> None:
        self.scroll_area = QScrollArea(self)
        self.scroll_content = QWidget()

        self.main_layout = QVBoxLayout(self)
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)

        self.main_layout.addWidget(self.scroll_area)

        self.db = database.get_cards()

    def generate_selected_cards(self, selected_cards: Counter) -> None:
        for entry in self.make_list_entries(selected_cards):
            self.scroll_content_layout.addWidget(entry, 0, Qt.AlignLeft)

        self.scroll_area.setWidget(self.scroll_content)
        self.selected_cards_generated = True

    def make_list_entries(self, cards: Counter) -> list:
        # create a sortet dictionary from Counter
        cards: dict = {k: v for k, v in sorted(dict(cards).items(), key=lambda item: self.db[f"{item[0]}"]["name"])}
        entries: list = []

        def make_entry():
            card_name = self.db[f"{card_id}"]["name"]
            item = QPushButton(text=f" {card_name} x{quantity}")

            item.setFlat(True)

            icon = QIcon()
            icon.addPixmap(QPixmap(f"{card_images.get_image_or_placeholder(card_id)}"))
            item.setIcon(icon)
            item.setIconSize(QSize(32, 48))
            
            item.clicked.connect(lambda: webbrowser.open(f"{generic_wiki_url}{card_name.replace('#', ' ')}"))

            entries.append(item)

        for (card_id, quantity) in cards.items():
            make_entry()

        return entries


class DraftSubWindow(QTabWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup()

    def setup(self) -> None:
        self.draft_tab = DraftTab()
        self.selected_cards_tab = SelectedCardsTab()

        self.addTab(self.draft_tab, "Draft")
        self.addTab(self.selected_cards_tab, "Selected cards")

