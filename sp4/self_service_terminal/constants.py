"""Constants for the whole project."""

from sp4.settings import BASE_DIR
from pathlib import Path

TITLE_LENGTH = 100
PRINTER = "some_name"
BUTTONS_PER_PAGE = 5
EXPORT_PATH = Path(BASE_DIR).parent.joinpath('export')
