## Vision-Based Desktop Automation

Windows desktop automation that grounds the Notepad icon via OpenCV template matching, launches it, and saves posts from JSONPlaceholder.

### Requirements
- Windows 10/11 at 1920x1080.
- Python 3.9.x.
- Desktop has a Notepad shortcut.

### Install (uv)
```bash
uv sync
```

### Install (pip)
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

### Notes
- The app minimizes windows (Win+D) before locating the icon.
- Configure thresholds and retries in `desktop/icon_detector.py` and `utils/retry.py`.
- On each run, the app asks you to **hover your mouse over the Notepad icon** on the desktop and press Enter; it captures a small patch around the cursor as the template and then searches the **entire desktop screenshot** for that icon.

### How to capture annotated screenshots (for the interview)
1) Move the Notepad icon to top-left, bottom-right, or center.
2) Run `python main.py`, let it detect and open Notepad.
3) Use `Win + Shift + S` (snipping tool) to manually capture and save screenshots showing the icon and the Notepad window; you can optionally extend the code to draw a box using `desktop.icon_detector.draw_debug_box`.

### Approach (for interview)
- Grounding: simple, interpretable multi-scale OpenCV template matching (`TM_CCOEFF_NORMED`) over the desktop screenshot, using a template captured from the live screen via the cursor.
- Robustness: retries with fixed backoff, desktop exposure via Win+D, and clear logging when the icon cannot be found.
- Automation: pyautogui for mouse/keyboard, pygetwindow to validate Notepad window titles, and overwrite-safe save flow with Enter confirmation.
- Extensibility: the same flow can capture any icon (hover over another icon/button instead of Notepad), and the search will still run over the full desktop; for more advanced robustness you can layer on OCR or feature-based methods later.
