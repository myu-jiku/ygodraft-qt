import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    root_dir: Path = Path(sys.executable).parent
elif __file__:
    root_dir: Path = Path(__file__).parent.parent

collection_dir: Path = root_dir / "collections"
images_dir: Path = root_dir / "images"
db_path: Path = root_dir / "card_db.json"
settings_path: Path = root_dir / "settings.json"

