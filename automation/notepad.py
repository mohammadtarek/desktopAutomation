import time
import os
from pathlib import Path
import pygetwindow as gw
from automation.mouse_keyboard import double_click, hotkey, press, type_text
from utils.logger import get_logger
import subprocess

logger = get_logger("notepad")


def open_notepad_via_icon(x: int, y: int) -> None:
    logger.info("Opening Notepad via icon at (%s, %s)", x, y)
    double_click(x, y)


def wait_for_notepad(timeout: float = 8.0) -> bool:
    end_time = time.time() + timeout
    while time.time() < end_time:
        # Check for 'Untitled - Notepad' specifically to ensure it's a fresh instance
        wins = gw.getWindowsWithTitle('Notepad')
        if wins:
            return True
        time.sleep(0.5)
    return False


def focus_notepad() -> bool:
    # Get the most recently opened Notepad window
    wins = gw.getWindowsWithTitle('Notepad')
    if wins:
        try:
            win = wins[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            return True
        except Exception as e:
            logger.warning(f"Could not focus Notepad: {e}")
    return False


def type_post_content(title: str, body: str) -> None:
    # Adding a small delay before typing to ensure focus is stable
    time.sleep(0.5)
    payload = f"Title: {title}\n\n{body}"
    type_text(payload)


def save_file(target_path: Path) -> None:
    # Ensure the target directory is clean
    if target_path.exists():
        target_path.unlink()

    hotkey("ctrl", "s")
    time.sleep(1.0)

    # Type the ABSOLUTE path to avoid saving in the last used folder
    type_text(str(target_path.absolute()))
    time.sleep(0.5)
    press("enter")
    time.sleep(1.0)


def force_cleanup_notepad():
    """Kills any running Notepad processes to ensure a clean state."""
    logger.info("Cleaning up any existing Notepad instances...")
    try:
        # This is the 'sledgehammer' approach to ensure no old windows are left
        subprocess.run(["taskkill", "/F", "/IM", "notepad.exe", "/T"],
                       capture_output=True, check=False)
        time.sleep(1)
    except Exception as e:
        logger.warning(f"Cleanup failed (might be no notepad running): {e}")


def close_notepad():
    """Targeted close of the current Notepad window."""
    wins = gw.getWindowsWithTitle('Notepad')
    for win in wins:
        try:
            win.close()
            time.sleep(0.5)
            # Handle 'Don't Save' if it pops up (though we should have saved already)
            press('n')
        except Exception:
            pass

    # If windows still exist, use the sledgehammer
    if gw.getWindowsWithTitle('Notepad'):
        force_cleanup_notepad()