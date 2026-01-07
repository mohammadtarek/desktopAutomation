import cv2
import numpy as np
from pathlib import Path
from desktop.icon_detector import IconNotFoundError

# Path to your saved template in the assets folder
TEMPLATE_PATH = Path(__file__).parent.parent /"artifacts" / "notepad_template.png"
_CACHED_TEMPLATE = None


def get_notepad_template():
    """Loads and caches the template from disk."""
    global _CACHED_TEMPLATE
    if _CACHED_TEMPLATE is None:
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Missing template: {TEMPLATE_PATH}. Save an icon snippet here first.")

        # Load in color (BGR)
        _CACHED_TEMPLATE = cv2.imread(str(TEMPLATE_PATH))

        if _CACHED_TEMPLATE is None:
            raise ValueError(f"Failed to decode image at {TEMPLATE_PATH}. Check if the file is a valid PNG.")

    return _CACHED_TEMPLATE


def locate_notepad_icon(screenshot):
    template = get_notepad_template()

    # Convert both to grayscale to ignore highlight colors
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < 0.8:
        raise IconNotFoundError(f"Icon not found. Confidence: {max_val:.2f}")

    h, w = template.shape[:2]
    return max_loc[0] + w // 2, max_loc[1] + h // 2, max_val


def set_notepad_template(template):
    """Optional: Allows updating the template in-memory if needed."""
    global _CACHED_TEMPLATE
    _CACHED_TEMPLATE = template