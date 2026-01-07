import time

import pyautogui

# Safety: allow failsafe corner
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def move_and_click(x: int, y: int, clicks: int = 1, interval: float = 0.1) -> None:
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click(clicks=clicks, interval=interval)


def double_click(x: int, y: int) -> None:
    move_and_click(x, y, clicks=2, interval=0.15)


def type_text(text: str, interval: float = 0.02) -> None:
    pyautogui.write(text, interval=interval)


def hotkey(*keys: str) -> None:
    pyautogui.hotkey(*keys)


def press(key: str) -> None:
    pyautogui.press(key)


def win_show_desktop() -> None:
    hotkey("win", "d")
    time.sleep(0.3)

def park_mouse():
    """Moves the mouse to a neutral corner to clear hovers/tooltips."""
    screen_width, screen_height = pyautogui.size()
    # Move to bottom right, but stay 10px away from the absolute corner to avoid FailSafe
    pyautogui.moveTo(screen_width - 10, screen_height - 10, duration=0.2)