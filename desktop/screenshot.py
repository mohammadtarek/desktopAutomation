from typing import Optional, Tuple

import mss
import numpy as np

from utils.logger import get_logger

logger = get_logger("screenshot")


def capture_desktop(region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
    """
    Capture a screenshot of the desktop. Region: (left, top, width, height).
    Returns BGR image as np.ndarray suitable for OpenCV.
    """
    try:
        with mss.mss() as sct:
            if region:
                # Convert tuple (x, y, w, h) to mss dict format
                left, top, width, height = region
                monitor = {"left": left, "top": top, "width": width, "height": height}
                logger.debug("Capturing region: %s", monitor)
            else:
                monitor = sct.monitors[1]
                logger.debug("Capturing full desktop monitor: %s", monitor)
            
            shot = sct.grab(monitor)
            img = np.array(shot)
            # mss returns BGRA; drop alpha
            return img[:, :, :3]
    except Exception as e:
        logger.error("Failed to capture screenshot. Region: %s, Error: %s", region, e)
        raise
