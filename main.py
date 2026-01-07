import sys
import time
from pathlib import Path

# ... (keep your existing imports) ...
from automation.mouse_keyboard import win_show_desktop
from automation.notepad import (
    close_notepad, focus_notepad, open_notepad_via_icon,
    save_file, type_post_content, wait_for_notepad,
)
from data.api_client import fetch_posts
from desktop.grounding import (
    capture_template_from_cursor, locate_notepad_icon, set_notepad_template,
)
from desktop.icon_detector import IconNotFoundError
from desktop.screenshot import capture_desktop
from utils.logger import get_logger, configure_logger

logger = get_logger(__name__)
OUTPUT_DIR = Path.home() / "Desktop" / "tjm-project"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", OUTPUT_DIR)


def initialize_notepad_template() -> None:
    """Show desktop and capture icon template."""
    win_show_desktop()
    time.sleep(1)  # Wait for desktop animation to finish
    input(
        "\n👉 Hover your mouse over the Notepad icon on the desktop,\n"
        "   then press [Enter] in this terminal to capture the template..."
    )
    template = capture_template_from_cursor()
    set_notepad_template(template)


def process_post(post: dict, idx: int) -> None:
    """Process a single post into a Notepad file."""
    win_show_desktop()
    time.sleep(0.5)
    screenshot = capture_desktop()

    try:
        x, y, score = locate_notepad_icon(screenshot)
        logger.info("Icon detected at (%s, %s) with confidence %.3f", x, y, score)
    except IconNotFoundError:
        logger.error("Could not find Notepad icon on the desktop using the captured template.")
        raise

    open_notepad_via_icon(x, y)

    if not wait_for_notepad():
        raise RuntimeError("Notepad did not launch in time.")

    focus_notepad()
    type_post_content(post.get("title", ""), post.get("body", ""))

    target_path = OUTPUT_DIR / f"post_{post.get('id')}.txt"
    save_file(target_path)

    close_notepad()
    time.sleep(1)  # Allow system time to close window before next loop


def main() -> int:
    configure_logger()
    ensure_output_dir()

    # 1. Calibrate (Template Matching)
    initialize_notepad_template()

    # 2. Fetch Data (Uses the robust fallback logic we built in api_client.py)
    # Changed limit to 10 to demonstrate automation loop
    posts = fetch_posts(limit=10)

    if not posts:
        logger.error("No posts found to process (API and Mock both failed).")
        return 1

    # 3. Process each post
    for idx, post in enumerate(posts, start=1):
        try:
            logger.info("--- Processing post %d/%d (ID: %s) ---", idx, len(posts), post.get("id"))
            process_post(post, idx)
        except Exception as exc:
            logger.error("Failed on post %s: %s", post.get("id"), exc)
            # We use 'continue' instead of 'return 1' so one failure doesn't stop the whole batch
            continue

    logger.info("Automation task complete. Processed %d posts.", len(posts))
    return 0


if __name__ == "__main__":
    sys.exit(main())