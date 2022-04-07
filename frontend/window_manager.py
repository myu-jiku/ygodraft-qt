from copy import deepcopy, copy

from PySide6.QtWidgets import (QWidget, QVBoxLayout)


class WindowManager(QWidget):
    root_window: QWidget
    void: QWidget
    layout: QVBoxLayout
    opened_windows: list

    def __init__(self, RootWindowClass: object) -> None:
        super().__init__()

        self.root_window = RootWindowClass()
        self.void = QWidget()
        self.root_layout = QVBoxLayout(self)
        self.opened_windows = []

        self.show_current_window()

    def go_back(self, steps: int = 1) -> None:
        if self.opened_windows:
            self.close_window()
            self.opened_windows = self.opened_windows[:-steps]
            self.show_current_window()

    def replace_window(self, new_window: QWidget, replace_count: int = 1) -> None:
        self.close_window()
        self.opened_windows = self.opened_windows[:-replace_count] + [new_window]
        self.show_current_window()

    def open_windows(self, *windows: QWidget) -> None:
        self.close_window()
        self.opened_windows = self.opened_windows + windows
        self.show_current_window()

    def open_window(self, window: QWidget) -> None:
        self.close_window()
        self.opened_windows.append(window)
        self.show_current_window()

    def close_all_windows(self) -> None:
        self.close_window()
        self.opened_windows = []
        self.show_current_window()

    def close_window(self) -> None:
        if self.opened_windows:
            self.opened_windows[-1].setParent(self.void)
        else:
            self.root_window.setParent(self.void)

    def get_current_widget(self) -> None:
        return self.root_layout.itemAt(0).widget()

    def show_current_window(self) -> None:
        if self.opened_windows:
            window = self.opened_windows[-1]
        else:
            window = self.root_window

        self.root_layout.addWidget(window)

