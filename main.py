import sys
import time
import traceback
from pathlib import Path

import pyautogui

from automation.mouse_keyboard import win_show_desktop, park_mouse
from automation.notepad import (
    close_notepad,
    focus_notepad,
    open_notepad_via_icon,
    save_file,
    type_post_content,
    wait_for_notepad,
    force_cleanup_notepad,
)
from data.api_client import fetch_posts
from desktop.grounding import locate_notepad_icon, get_notepad_template
from desktop.icon_detector import IconNotFoundError
from desktop.screenshot import capture_desktop
from utils.logger import get_logger, configure_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path.home() / "Desktop" / "tjm-project"


def ensure_output_dir() -> None:
    """Creates the target directory for saved .txt files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", OUTPUT_DIR)


def process_post(post: dict, idx: int, total: int) -> bool:
    """
    Process a single post. Returns True if successful, False otherwise.
    """
    post_id = post.get('id', idx)

    logger.info("=" * 70)
    logger.info(f"POST {idx}/{total} - ID: {post_id}")
    logger.info("=" * 70)

    try:
        # STEP 1: Clean slate
        logger.info("STEP 1: Clearing desktop...")
        force_cleanup_notepad()  # Kill any lingering Notepad instances
        time.sleep(1.0)

        win_show_desktop()
        park_mouse()
        time.sleep(1.5)

        # STEP 2: Find icon
        logger.info("STEP 2: Locating Notepad icon...")
        screenshot = capture_desktop()
        x, y, score = locate_notepad_icon(screenshot,iteration_idx=idx)
        logger.info(f"✓ Icon found at ({x}, {y}) - confidence: {score:.3f}")

        # STEP 3: Open Notepad
        logger.info("STEP 3: Opening Notepad...")
        open_notepad_via_icon(x, y)

        if not wait_for_notepad(timeout=10):
            logger.error("✗ Notepad failed to open")
            return False

        # STEP 4: Focus window
        logger.info("STEP 4: Focusing Notepad window...")
        if not focus_notepad():
            logger.error("✗ Could not focus Notepad")
            return False

        time.sleep(1.0)  # Extra wait to ensure focus is stable

        # STEP 5: Type content
        logger.info("STEP 5: Typing content...")
        type_post_content(
            post.get("title", "No Title"),
            post.get("body", "No Body")
        )

        # STEP 6: Save file
        logger.info("STEP 6: Saving file...")
        target_path = OUTPUT_DIR / f"post_{post_id}.txt"

        save_success = save_file(target_path)

        if not save_success:
            logger.error(f"✗ Failed to save post_{post_id}.txt")
            return False

        # STEP 7: Close Notepad
        logger.info("STEP 7: Closing Notepad...")
        close_notepad()
        time.sleep(0.5)
        pyautogui.click(5, 5)
        time.sleep(0.5)
        logger.info(f"✓✓✓ Post {post_id} completed successfully!")
        return True

    except IconNotFoundError as e:
        logger.error(f"✗ Icon detection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        traceback.print_exc()
        return False


def main() -> int:
    configure_logger()
    ensure_output_dir()

    logger.info("=" * 70)
    logger.info("🚀 DESKTOP AUTOMATION - NOTEPAD FILE CREATOR")
    logger.info("=" * 70)

    # Initial cleanup
    logger.info("Performing initial cleanup...")
    force_cleanup_notepad()
    time.sleep(2)

    # Load template
    try:
        get_notepad_template()
        logger.info("✓ Template loaded")
    except Exception as e:
        logger.error(f"✗ Template load failed: {e}")
        return 1

    # Fetch posts
    logger.info("Fetching posts from API...")
    posts = fetch_posts(limit=10)

    if not posts:
        logger.error("✗ No posts retrieved")
        return 1

    logger.info(f"✓ Retrieved {len(posts)} posts\n")

    # Process each post
    results = []
    for idx, post in enumerate(posts, start=1):
        success = process_post(post, idx, len(posts))
        results.append(success)

        # Short break between posts
        time.sleep(1)

    # Final cleanup
    force_cleanup_notepad()

    success_count = sum(results)

    # List created files
    created_files = sorted(OUTPUT_DIR.glob("post_*.txt"))
    logger.info(f"\n📄 Created {len(created_files)} files:")
    for f in created_files:
        logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")

    logger.info("=" * 70)

    return 0 if success_count == len(posts) else 1


if __name__ == "__main__":
    sys.exit(main())