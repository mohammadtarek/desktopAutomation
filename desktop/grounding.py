from typing import Optional, Tuple

import numpy as np
import pyautogui

from desktop.icon_detector import IconNotFoundError, match_template_multiscale
from desktop.screenshot import capture_desktop
from utils.logger import get_logger
from utils.retry import retry

logger = get_logger("grounding")

# Global cache of the Notepad template, captured once from the user's desktop.
_NOTEPAD_TEMPLATE: Optional[np.ndarray] = None

DEFAULT_SCALES = (0.9, 1.0, 1.1)
DEFAULT_THRESHOLD = 0.75
# Exclude taskbar (assume ~40px) and top strip (20px) from search
DESKTOP_SEARCH_REGION = (0, 20, 1920, 1040)  # (x, y, w, h)


def capture_template_from_cursor(box_size: int = 80) -> np.ndarray:
    """
    Capture a small square patch around the current mouse cursor.
    The user should hover the cursor over the Notepad icon before this is called.
    """
    import time
    
    x, y = pyautogui.position()
    half = box_size // 2
    
    # Get screen dimensions to ensure region stays within bounds
    screen_width, screen_height = pyautogui.size()
    
    # Clamp the region to screen boundaries
    left = max(0, x - half)
    top = max(0, y - half)
    right = min(screen_width, x + half)
    bottom = min(screen_height, y + half)
    
    # Calculate actual width and height (may be smaller if near edges)
    width = right - left
    height = bottom - top
    
    # Ensure minimum size
    if width < 40 or height < 40:
        raise ValueError(
            f"Cursor too close to screen edge. Please move cursor more to center. "
            f"Current position: ({x}, {y}), Screen size: {screen_width}x{screen_height}"
        )
    
    region = (left, top, width, height)
    logger.info("Capturing template around cursor at (%s, %s) with region %s", x, y, region)
    
    # Small delay to ensure desktop is stable
    time.sleep(0.2)
    
    return capture_desktop(region)


def set_notepad_template(template_bgr: np.ndarray) -> None:
    """
    Store the captured Notepad template for later matching.
    """
    global _NOTEPAD_TEMPLATE
    _NOTEPAD_TEMPLATE = template_bgr
    logger.info("Notepad template initialized (shape=%s)", template_bgr.shape)


@retry(attempts=3, delay_seconds=1.0, exceptions=(IconNotFoundError,))
def locate_notepad_icon(
    screenshot_bgr: np.ndarray,
    scales=DEFAULT_SCALES,
    threshold: float = DEFAULT_THRESHOLD,
    search_region: Optional[Tuple[int, int, int, int]] = DESKTOP_SEARCH_REGION,
) -> Tuple[int, int, float]:
    """
    Locate the Notepad icon and return (x, y, score) using the cached template.
    Retries handled via decorator.
    """
    if _NOTEPAD_TEMPLATE is None:
        raise RuntimeError("Notepad template has not been initialized.")

    return match_template_multiscale(
        screenshot_bgr,
        _NOTEPAD_TEMPLATE,
        scales=scales,
        threshold=threshold,
        search_region=search_region,
    )
