import time
from pathlib import Path
from typing import Optional

import pygetwindow as gw

from automation.mouse_keyboard import double_click, hotkey, press, type_text
from utils.logger import get_logger

logger = get_logger("notepad")


def open_notepad_via_icon(x: int, y: int) -> None:
    logger.info("Opening Notepad via icon at (%s, %s)", x, y)
    double_click(x, y)


def wait_for_notepad(timeout: float = 8.0) -> bool:
    """
    Poll for a window containing 'Notepad' in the title.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        wins = gw.getAllTitles()
        if any("Notepad" in title for title in wins if title.strip()):
            return True
        time.sleep(0.3)
    return False


def focus_notepad() -> bool:
    for win in gw.getAllWindows():
        if "Notepad" in win.title:
            try:
                win.activate()
                return True
            except Exception:
                continue
    return False


def type_post_content(title: str, body: str) -> None:
    payload = f"Title: {title}\n\n{body}"
    type_text(payload)


def save_file(target_path: Path) -> None:
    hotkey("ctrl", "s")
    time.sleep(0.5)
    type_text(str(target_path))
    press("enter")
    time.sleep(0.6)
    # handle overwrite confirmation: Enter
    press("enter")


def close_notepad() -> None:
    hotkey("alt", "f4")
    time.sleep(0.3)
    # If prompted to save, hit don't save (N) or Enter assuming saved.
    press("enter")
