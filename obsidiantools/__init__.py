import logging

from . import api as api
from . import canvas_utils as canvas_utils
from . import html_processing as html_processing
from . import md_utils as md_utils
from . import media_utils as media_utils


def enable_debug(level: int = logging.DEBUG) -> None:
    """Enable debug logging for obsidiantools.

    Usage:
        import obsidiantools
        obsidiantools.enable_debug()  # DEBUG level
        obsidiantools.enable_debug(logging.INFO)  # INFO level only
    """
    pkg_logger = logging.getLogger("obsidiantools")
    pkg_logger.setLevel(level)
    if not pkg_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        pkg_logger.addHandler(handler)
