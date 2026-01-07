from pathlib import Path
from typing import Iterable, Optional, Tuple

import cv2
import numpy as np

from utils.logger import get_logger

logger = get_logger("icon_detector")


class IconNotFoundError(RuntimeError):
    pass


def load_template(template_path: Path) -> np.ndarray:
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at {template_path}")
    template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(f"Failed to load template: {template_path}")
    return template


def match_template_multiscale(
    screenshot_bgr: np.ndarray,
    template_bgr: np.ndarray,
    scales: Iterable[float] = (0.9, 1.0, 1.1),
    threshold: float = 0.75,
    search_region: Optional[Tuple[int, int, int, int]] = None,
) -> Tuple[int, int, float]:
    """
    Return (center_x, center_y, best_score) using multi-scale template matching.
    search_region optional (x, y, w, h) to crop screenshot before matching.
    Raises IconNotFoundError on failure.
    """
    screenshot = screenshot_bgr
    offset_x = 0
    offset_y = 0
    if search_region:
        x, y, w, h = search_region
        screenshot = screenshot[y : y + h, x : x + w]
        offset_x, offset_y = x, y

    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    best_score = -1.0
    best_center: Optional[Tuple[int, int]] = None

    for scale in scales:
        scaled_template = cv2.resize(
            template_bgr, dsize=None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA
        )
        gray_template = cv2.cvtColor(scaled_template, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > best_score:
            best_score = max_val
            best_center = (
                max_loc[0] + gray_template.shape[1] // 2 + offset_x,
                max_loc[1] + gray_template.shape[0] // 2 + offset_y,
            )
        logger.debug(
            "Scale %.2f -> max score %.4f at %s", scale, max_val, max_loc
        )

    if best_score < threshold or best_center is None:
        raise IconNotFoundError(
            f"No match above threshold {threshold} (best={best_score:.3f})"
        )

    return best_center[0], best_center[1], best_score


def draw_debug_box(
    screenshot_bgr: np.ndarray,
    center: Tuple[int, int],
    template_shape: Tuple[int, int, int],
    color: Tuple[int, int, int] = (0, 0, 255),
) -> np.ndarray:
    """
    Draw bounding box and center point for visualization.
    """
    h, w = template_shape[:2]
    cx, cy = center
    top_left = (int(cx - w / 2), int(cy - h / 2))
    bottom_right = (int(cx + w / 2), int(cy + h / 2))
    annotated = screenshot_bgr.copy()
    cv2.rectangle(annotated, top_left, bottom_right, color, 2)
    cv2.circle(annotated, (cx, cy), 5, color, -1)
    return annotated
