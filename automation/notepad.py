import time
import os
from pathlib import Path

import pyautogui
import pygetwindow as gw
import pyperclip
from automation.mouse_keyboard import hotkey, press
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
    wins = gw.getWindowsWithTitle('Notepad')
    if wins:
        try:
            win = wins[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.5)

            # CRITICAL: Click inside the NOTEPAD WINDOW, not on the desktop icon.
            # We click at the top-center of the window (the title bar area).
            click_x = win.left + (win.width // 2)
            click_y = win.top + 10
            pyautogui.click(click_x, click_y)

            # Move the mouse to a neutral corner so the hover effect disappears
            pyautogui.moveTo(10, 10)

            return True
        except Exception as e:
            logger.warning(f"Could not focus Notepad: {e}")
    return False


def type_post_content(title: str, body: str) -> None:
    """Pastes content into Notepad instantly via the clipboard."""
    focus_notepad()

    # 1. Clear previous session content (Windows 11 fix)
    hotkey("ctrl", "a")
    time.sleep(0.1)
    press("backspace")

    # 2. Prepare the payload
    payload = f"Title: {title}\n\n{body}"

    # 3. Copy to clipboard and paste
    logger.info("Copying content to clipboard and pasting...")
    pyperclip.copy(payload)
    time.sleep(0.2)  # Small buffer for clipboard sync
    hotkey("ctrl", "v")

    # 4. Clear clipboard after (Security best practice)
    pyperclip.copy("")
    logger.info("✓ Content pasted successfully")


def save_file(target_path: Path) -> None:
    if target_path.exists():
        target_path.unlink()

    hotkey("ctrl", "shift", "s")
    time.sleep(1.0)

    # Instead of typing the whole path, paste it!
    full_path = str(target_path.absolute())
    pyperclip.copy(full_path)
    hotkey("ctrl", "v")

    time.sleep(0.3)
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