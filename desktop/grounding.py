import cv2
import numpy as np
from pathlib import Path
from desktop.icon_detector import IconNotFoundError

# Setup Debug Directory
DEBUG_DIR = Path.home() / "Desktop" / "tjm-project" / "debug_screenshots"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_PATH = Path(__file__).parent.parent / "artifacts" / "notepad_template.png"
_CACHED_TEMPLATE = None


def get_notepad_template():
    global _CACHED_TEMPLATE
    if _CACHED_TEMPLATE is None:
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")
        _CACHED_TEMPLATE = cv2.imread(str(TEMPLATE_PATH))
    return _CACHED_TEMPLATE


def locate_notepad_icon(screenshot, iteration_idx=0):
    # 1. Load template and get edges
    template = get_notepad_template()
    template_edges = cv2.Canny(template, 50, 200)
    (tH, tW) = template.shape[:2]

    # 2. Convert screenshot to grayscale and get edges
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    found = None

    # 3. Loop over scales to find Large, Medium, or Small views
    # We search from 40% of original size to 300% of original size
    for scale in np.linspace(0.4, 3.0, 30):
        # Resize screenshot according to scale
        resized_w = int(gray_screen.shape[1] * scale)
        resized = cv2.resize(gray_screen, (resized_w, int(gray_screen.shape[0] * scale)))
        ratio = gray_screen.shape[1] / float(resized.shape[1])

        # If resized image is smaller than template, break
        if resized.shape[0] < tH or resized.shape[1] < tW:
            continue

        # Detect edges in resized image
        screen_edges = cv2.Canny(resized, 50, 200)
        result = cv2.matchTemplate(screen_edges, template_edges, cv2.TM_CCOEFF_NORMED)
        (_, max_val, _, max_loc) = cv2.minMaxLoc(result)

        # Keep track of the best match
        if found is None or max_val > found[0]:
            found = (max_val, max_loc, ratio)

    # 4. Final Evaluation
    (max_val, max_loc, ratio) = found

    # Threshold is lower (0.2 - 0.5) for Edge Matching as it's more strict
    if max_val < 0.25:
        cv2.imwrite(str(DEBUG_DIR / f"failed_view_change_{iteration_idx}.png"), screenshot)
        raise IconNotFoundError(f"Icon not found. Even at different scales, max match was {max_val:.2f}")

    # Map back to original coordinates
    startX = int(max_loc[0] * ratio)
    startY = int(max_loc[1] * ratio)
    endX = int((max_loc[0] + tW) * ratio)
    endY = int((max_loc[1] + tH) * ratio)

    center_x = (startX + endX) // 2
    center_y = (startY + endY) // 2

    # --- SAVE DEBUG IMAGE ---
    debug_img = screenshot.copy()
    cv2.rectangle(debug_img, (startX, startY), (endX, endY), (0, 255, 0), 3)
    cv2.putText(debug_img, f"View detected Score: {max_val:.2f}", (startX, startY - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imwrite(str(DEBUG_DIR / f"view_match_{iteration_idx}.png"), debug_img)

    return center_x, center_y, max_val