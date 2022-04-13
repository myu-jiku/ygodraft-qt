import sys
from pathlib import Path

from PySide6.QtGui import (QIcon)

from backend import paths


class Icon(QIcon):
    def __init__(self, image: str) -> None:
        super().__init__()

        if hasattr(sys, "_MEIPASS"):
            self.addFile((Path(sys._MEIPASS) / "images" / image).as_posix())
        else:
            self.addFile((paths.images_dir / image).as_posix())

