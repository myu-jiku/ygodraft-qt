import webbrowser

from collections import Counter
from PySide6 import QtWidgets, QtCore, QtGui

from backend import card_images
from backend import database
from backend import draft


generic_wiki_url: str = "https://yugipedia.com/wiki/"


class DraftTab(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup()

    def setup(self) -> None:
        self.choices_tool_box = QtWidgets.QToolBox()
        self.confirm_button = QtWidgets.QPushButton(text="Confirm")

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.main_layout.addWidget(self.choices_tool_box)
        self.main_layout.addWidget(self.confirm_button)

    def generate_choices(self, choices: list) -> None:
        for index, choice in enumerate(choices):
            page = QtWidgets.QWidget()
            page_layout = QtWidgets.QHBoxLayout(page)

            for card_id in choice:
                page_layout.addWidget(self.make_card(card_id))

            self.choices_tool_box.addItem(page, f"Choice {index + 1}")

    def make_card(self, card_id: int) -> QtWidgets.QPushButton:
        card = QtWidgets.QPushButton()
        card.setFocusPolicy(QtCore.Qt.NoFocus)

        card.setIconSize(QtCore.QSize(168, 246))
        card.setMaximumSize(QtCore.QSize(176, 254))

        card.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        image = QtGui.QIcon()
        image.addPixmap(
            QtGui.QPixmap(f"{card_images.get_image_or_placeholder(card_id)}"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )

        card.setIcon(image)

        card_name = database.get_cards()[f"{card_id}"]["name"]
        card.clicked.connect(lambda: webbrowser.open(f"{generic_wiki_url}{card_name.replace('#', ' ')}"))
        card.setToolTip(f"{card_name} (view on Yugipedia)")

        return card


class SelectedCardsTab(QtWidgets.QWidget):
    selected_cards_generated: bool = False

    def __init__(self) -> None:
        super().__init__()
        self.setup()

    def setup(self) -> None:
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_content = QtWidgets.QWidget()

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.scroll_content_layout = QtWidgets.QVBoxLayout(self.scroll_content)

        self.main_layout.addWidget(self.scroll_area)

        self.db = database.get_cards()

    def generate_selected_cards(self, selected_cards: Counter) -> None:
        for entry in self.make_list_entries(selected_cards):
            self.scroll_content_layout.addWidget(entry, 0, QtCore.Qt.AlignLeft)

        self.scroll_area.setWidget(self.scroll_content)
        self.selected_cards_generated = True

    def make_list_entries(self, cards: Counter) -> list:
        # create a sortet dictionary from Counter
        cards: dict = {k: v for k, v in sorted(dict(cards).items(), key=lambda item: self.db[f"{item[0]}"]["name"])}
        entries: list = []

        def make_entry():
            card_name = self.db[f"{card_id}"]["name"]
            item = QtWidgets.QPushButton(text=f" {card_name} x{quantity}")

            item.setFlat(True)

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(f"{card_images.get_image_or_placeholder(card_id)}"))
            item.setIcon(icon)
            item.setIconSize(QtCore.QSize(32, 48))
            
            item.clicked.connect(lambda: webbrowser.open(f"{generic_wiki_url}{card_name.replace('#', ' ')}"))

            entries.append(item)

        for (card_id, quantity) in cards.items():
            make_entry()

        return entries


class DraftSubWindow(QtWidgets.QTabWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup()

    def setup(self) -> None:
        self.draft_tab = DraftTab()
        self.selected_cards_tab = SelectedCardsTab()

        self.addTab(self.draft_tab, "Draft")
        self.addTab(self.selected_cards_tab, "Selected cards")

