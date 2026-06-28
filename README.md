# Helldivers 2 - Dynamic Stream Deck Macro Suite

An optimized, lightweight, and hardware-safe automation layer for Helldivers 2. This project utilizes computer vision to dynamically analyze your live in-game stratagem loadout from a 4K viewport, updates custom Stream Deck icon layouts on the fly, and fires low-level hardware keyboard scancodes to execute stratagems safely beneath anti-cheat detection layers.

## 🛠️ The Architecture
1. **`main.py` (The Scanner):** Fired directly by your "Scan Loadout" key on the Stream Deck. It instantly wakes up, takes a screenshot, crops your 4 active stratagem slots, uses OpenCV template matching to resolve what you have equipped, updates the localized asset state, and immediately shuts down (**0.0% idle CPU footprint**).
2. **`press_slot.py` (The Executor):** The master macro processing suite. When you press an active slot key on your Stream Deck, it reads the current state file and builds low-level Windows API keyboard inputs using direct hardware scancodes (`ctypes.windll.user32.SendInput`).
3. **`slotX.py` (The Wrappers):** Independent, fast-booting entry points mapped to each physical Stream Deck button that safely call the execution engine with their corresponding slot indexes.

---

## 🛡️ Built-In Combat Safety Engines

To protect gameplay integrity and ensure absolute stability during intense matches, the codebase implements two critical hardware-level safety layers:

### 1. OpenCV Misclick Protection Layer (`main.py`)
If you accidentally hit your scan button while navigating map screens, reading chat windows, or sitting in a pause menu, the system automatically runs a signature threshold validation before altering your profile files:
* Every cropped slot must score a normalized correlation coefficient match higher than `0.65` against your template folder database to count as recognized.
* **The Threshold Rule:** The script requires at least **2 out of 4 slots** to be resolved with high confidence. 
* If you scan a random screen, the script flags a low matching signature threshold and safely aborts the execution loop—completely preserving your last known valid loadout and active icons on your desk.

---

## 📂 Repository Workspace Mapping

* `main.py` — Core entry point for localized computer vision screen capture and template analysis.
* `press_slot.py` — Master scancode generation layer protected by the Win32 Kernel Mutex lock.
* `slot0.py` through `slot3.py` — Lightweight Stream Deck hardware execution triggers.
* `active_slot_0.png` through `active_slot_3.png` — The active stratagems detected by `main.py`.
* `templates/` — Database directory holding reference `.png` profile icons for every in-game stratagem.
* `current_loadout.txt` — Real-time plaintext tracking state shared between the scanner and macro engines.
* `debug_log.txt` — Diagnostic main.py.
* `macro_log.txt` — Diagnostic press_slot.py.
