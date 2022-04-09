from PySide6.QtCore import (Signal, Qt)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QLabel)


class CardSetButton(QWidget):
    labels: dict = None
    selected: bool = False
    switched = Signal()

    def __init__(self, set_data: dict) -> None:
        self.labels = self.labels or {}
    
        super().__init__()
        self.init_gui()
        self.set_gui_parameters()
        self.generate_labels(set_data)

    def init_gui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        
        self.frame = QFrame()
        self.frame_layout = QHBoxLayout(self.frame)
        self.main_layout.addWidget(self.frame)

    def set_gui_parameters(self) -> None:
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.frame.setFrameShape(self.frame.Panel)
        self.frame.setFrameShadow(self.frame.Raised)

    def generate_labels(self, set_data: dict) -> None:
        first_widget: bool = True

        for label, data in set_data.items():
            widget = QLabel(data)
            widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

            if first_widget:
                self.setToolTip(data)
                first_widget = False
            else:
                widget.setAlignment(Qt.AlignCenter)

                line = QFrame()
                line.setFrameShape(line.VLine)
                line.setFrameShadow(line.Raised)
                self.frame_layout.addWidget(line)

            self.labels[label] = widget
            
            self.frame_layout.addWidget(self.labels[label])

    def update_frame_style(self) -> None:
        self.frame.setFrameShape([self.frame.Panel, self.frame.Box][self.selected])
        self.frame.setFrameShadow([self.frame.Raised, self.frame.Plain][self.selected])

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected = not self.selected
            self.update_frame_style()
            self.switched.emit()
