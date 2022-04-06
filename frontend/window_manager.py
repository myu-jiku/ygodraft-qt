from copy import deepcopy, copy

from PySide6 import QtWidgets


class WindowManager(QtWidgets.QWidget):
    root_window: QtWidgets.QWidget
    void: QtWidgets.QWidget
    layout: QtWidgets.QVBoxLayout
    opened_windows: list

    def __init__(self, RootWindowClass: object) -> None:
        super().__init__()

        self.root_window = RootWindowClass()
        self.void = QtWidgets.QWidget()
        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.opened_windows = []

        self.show_current_window()

    def go_back(self, steps: int = 1) -> None:
        self.close_window()
        self.opened_windows = self.opened_windows[:-steps]
        self.show_current_window()

    def replace_window(self, new_window: QtWidgets.QWidget, replace_count: int = 1) -> None:
        self.close_window()
        self.opened_windows = self.opened_windows[:-replace_count] + [new_window]
        self.show_current_window()

    def open_windows(self, *windows: QtWidgets.QWidget) -> None:
        self.close_window()
        self.opened_windows = self.opened_windows + windows
        self.show_current_window()

    def open_window(self, window: QtWidgets.QWidget) -> None:
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

