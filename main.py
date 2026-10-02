import time
import cv2
import numpy as np
import keyboard
import os
import shutil
from PIL import ImageGrab
import socket
import sys
import base64

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)  

# SINGLE INSTANCE LOCK: Prevents accidental spamming of the scan process
try:
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lock_socket.bind(("127.0.0.1", 45678)) 
except socket.error:
    sys.exit(0)


# --- LIVE DEBUG LOGGER ---
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout if sys.stdout is not None else None
        self.log = open("debug_log.txt", "w", encoding="utf-8", buffering=1)

    def write(self, message):
        if self.terminal is not None:
            try: self.terminal.write(message)
            except Exception: pass
        self.log.write(message)
        
    def flush(self):
        if self.terminal is not None:
            try: self.terminal.flush()
            except Exception: pass
        self.log.flush()

sys.stdout = Logger()
sys.stderr = Logger()

# Clear last session's macro log too, since press_slot.py appends to it
# per-press (separate short-lived processes) rather than owning one
# long-lived handle like this process does for debug_log.txt.
try:
    open("macro_log.txt", "w", encoding="utf-8").close()
except Exception:
    pass


# --- CONFIGURATION ---
STRATAGEM_MENU_KEY = "ctrl"  
ARROW_MAPPING = {
    "up": "numpad8",
    "down": "numpad5",
    "left": "numpad4",
    "right": "numpad6"
}

STRATAGEMS = {

    # == SUPPORT WEAPONS == 
    "HD2-MG": ["down", "left", "down", "up", "right"],                           # MG-43 Machine Gun
    "HD2-EAT": ["down", "down", "left", "up", "right"],                          # EAT-17 Expendable Anti-Tank
    "HD2-STA": ["down", "left", "down", "up", "up", "left"],                     # M-105 Stalwart
    "HD2-LC": ["down", "left", "down", "up", "left"],                            # LAS-98 Laser Cannon
    "HD2-AMR": ["down", "left", "right", "up", "down"],                          # APW-1 Anti-Materiel Rifle
    "HD2-GL": ["down", "left", "up", "left", "down"],                            # GL-21 Grenade Launcher
    "HD2-RR": ["down", "left", "right", "right", "left"],                        # GR-8 Recoilless Rifle
    "HD2-FT": ["down", "left", "up", "down", "up"],                              # FLAM-40 Flamethrower
    "HD2-HMG": ["down", "left", "up", "down", "down"],                           # MG-206 Heavy Machine Gun
    "HD2-AC": ["down", "left", "down", "up", "up", "right"],                     # AC-8 Autocannon
    "HD2-AT": ["down", "right", "down", "up", "left", "left"],                   # ARC-3 Arc Thrower
    "HD2-QC": ["down", "down", "up", "left", "right"],                           # LAS-99 Quasar Cannon
    "HD2-ABR": ["down", "up", "up", "left", "right"],                            # RL-77 Airburst Rocket Launcher
    "HD2-MLS": ["down", "left", "up", "down", "right"],                          # MLS-4X Commando
    "HD2-SPE": ["down", "down", "up", "down", "down"],                           # FAF-14 Spear
    "HD2-RG": ["down", "right", "left", "down", "up", "left", "right"],          # RS-422 Railgun
    "HD2-WAS": ["down", "down", "up", "down", "right"],                          # StA-X3 W.A.S.P. Launcher 
    "HD2-BREHAM": ["down", "left", "right", "left", "up"],                       # CQC-20 Breaching Hammer 	
    "HD2-EPO": ["down", "left", "up", "left", "right"],                          # PLAS-45 Epoch 
    "HD2-MGX": ["down", "left", "down", "right", "up", "left"],                  # MGX-42 Bullet Storm 
    "HD2-SPR": ["down", "right", "down", "left", "up", "right"],                 # S-11 Speargun
    "HD2-DEFO": ["down", "left", "right", "right", "down"],                      # CQC-9 Defoliation Tool
    "HD2-STE": ["down", "left", "up", "down", "left"],                           # TX-41 Sterilizer
    "HD2-EXN": ["down", "down", "left", "up", "left"],                           # EAT-700 Expendable Napalm
    "HD2-EAT411": ["down", "down", "left", "up", "down"],                        # EAT-411 Leveller 
    "HD2-DEE": ["down", "right", "up", "left", "right"],                         # GL-52 De-Escalator
    "HD2-BELTGREN": ["down", "left", "up", "left", "up", "up"],                  # GL-28 Belt-Fed Grenade Launcher 
    "HD2-BMDC4": ["down", "right", "up", "up", "right", "up"],                   # B/MD C4 Pack
    "HD2-SLO": ["down", "up", "right", "down", "down"],                          # MS-11 Solo Silo
    "HD2-CRE": ["down", "down", "right", "down", "up", "up"],                    # B/FLAM-80 Cremator
    "HD2-MAXG": ["down", "left", "right", "down", "up", "up"],                   # M-1000 Maxigun
    "HD2-OTF": ["down", "left", "right", "right", "up"],                         # CQC-1 One True Flag
    
    # == ORBITAL STRIKES ==
    "HD2-OPS": ["right", "right", "up"],                                         # Orbital Precision Strike
    "HD2-EGB": ["right", "down", "left", "up", "up"],                            # Orbital Gatling Barrage                    
    "HD2-OGS": ["right", "right", "down", "right"],                              # Orbital Gas Strike
    "HD2-O120": ["right", "right", "down", "left", "right", "down"],             # Orbital 120mm HE Barrage
    "HD2-OAS": ["right", "right", "right"],                                      # Orbital Airburst Strike
    "HD2-OSS": ["right", "right", "down", "up"],                                 # Orbital Smoke Strike
    "HD2-OES": ["right", "right", "left", "down"],                               # Orbital EMS Strike
    "HD2-O380": ["right", "down", "up", "up", "left", "down", "down"],           # Orbital 380mm HE Barrage
    "HD2-OWB": ["right", "down", "right", "down", "right", "down"],              # Orbital Walking Barrage
    "HD2-OL": ["right", "down", "up", "right", "down"],                          # Orbital Laser
    "HD2-ONB": ["right", "right", "down", "left", "right", "up"],                # Orbital Napalm Barrage
    "HD2-ORS": ["right", "up", "down", "down", "right"],                         # Orbital Railcannon Strike

    # == EAGLE STRIKES ==
    "HD2-ESR": ["up", "right", "right"],                                         # Eagle Strafing Run
    "HD2-EA": ["up", "right", "down", "right"],                                  # Eagle Airstrike 
    "HD2-ECB": ["up", "right", "down", "down", "right"],                         # Eagle Cluster Bomb
    "HD2-ESS": ["up", "right", "up", "down"],                                    # Eagle Smoke Strike
    "HD2-ENA": ["up", "right", "down", "up"],                                    # Eagle Napalm Airstrike
    "HD2-E110": ["up", "right", "up", "left"],                                   # Eagle 110mm Rocket Pods
    "HD2-E500": ["up", "right", "down", "down", "down"],                         # Eagle 500kg Bomb

    # == EMPLACEMENTS ==
    "HD2-APM": ["down", "left", "up", "right"],                                  # MD-6 Anti-Personnel Minefield
    "HD2-IM": ["down", "left", "left", "down"],                                  # MD-I4 Incendiary Mines
    "HD2-ATM": ["down", "left", "up", "up"],                                     # MD-17 Anti-Tank Mines 
    "HD2-SG": ["down", "down", "left", "right", "left", "right"],                # FX-12 Shield Generator Relay
    "HD2-HMGT": ["down", "up", "left", "right", "right", "left"],                # E/MG-101 HMG Emplacement
    "HD2-GRB": ["down", "right", "down", "left", "right"],                       # E/GL-21 Grenadier Battlement
    "HD2-MD8": ["down", "left", "left", "right"],                                # MD-8 Gas Mines 
    "HD2-ATE": ["down", "up", "right", "right", "left"],                         # E/AT-12 Anti-Tank Emplacement
    "HD2-TT": ["down", "up", "right", "up", "left", "right"],                    # A/ARC-3 Tesla Tower
    
    # == SENTRIES ==
    "HD2-MGS": ["down", "up", "right", "right", "up"],                           # A/MG-43 Machine Gun Sentry
    "HD2-GS": ["down", "up", "right", "left"],                                   # A/G-16 Gatling Sentry
    "HD2-AS": ["down", "up", "right", "up", "left", "up"],                       # A/AC-8 Autocannon Sentry 
    "HD2-MS": ["down", "up", "right", "right", "down"],                          # A/M-12 Mortar Sentry
    "HD2-RS": ["down", "up", "right", "right", "left"],                          # A/MLS-4X Rocket Sentry
    "HD2-EMS": ["down", "up", "right", "down", "right"],                         # A/M-23 EMS Mortar Sentry
    "HD2-LSE": ["down", "up", "right", "down", "up", "right"],                   # A/LAS-98 Laser Sentry 	
    "HD2-FS": ["down", "up", "right", "down", "up", "up"],                       # A/FLAM-40 Flame Sentry
    "HD2-GMS": ["down", "up", "right", "down", "right"],                         # A/GM-17 Gas Mortar Sentry
    
    # == BACKPACKS == 
    "HD2-SP": ["down", "left", "down", "up", "up", "down"],                      # B-1 Supply Pack
    "HD2-JP": ["down", "up", "up", "down", "up"],                                # LIFT-850 Jump Pack
    "HD2-BS": ["down", "left", "down", "down", "up", "left"],                    # SH-20 Ballistic Shield Backpack
    "HD2-SGP": ["down", "up", "left", "right", "left", "right"],                 # SH-32 Shield Generator Pack
    "HD2-DS": ["down", "up", "left", "right", "up", "up"],                       # SH-51 Directional Shield
    "HD2-PHB": ["down", "right", "up", "up", "up"],                              # B-100 Portable Hellbomb
    "HD2-HP": ["down", "up", "up", "down", "left", "right"],                     # LIFT-860 Hover Pack
    "HD2-WP": ["down", "left", "right", "down", "left", "right"],                # LIFT-182 Warp Pack
    "HD2-GD": ["down", "up", "left", "up", "right", "down"],                     # AX/AR-23 Guard Dog
    "HD2-GDR": ["down", "up", "left", "up", "right", "right"],                   # AX/LAS-5 Rover
    "HD2-GDHD": ["down", "up", "left", "up", "left", "left"],                    # AX/FLAM-75 Hot Dog
    "HD2-GDK9": ["down", "up", "left", "up", "right", "left"],                   # AX/ARC-3 K-9
    "HD2-GDDB": ["down", "up", "left", "up", "right", "up"],                     # AX/TX-13 Dog Breath
    
    # == VEHICLES == 
    "HD2-EXO2": ["left", "down", "right", "up", "left", "down", "up"],                      # EXO-49 Emancipator Exosuit
    "HD2-EXO": ["left", "down", "right", "up", "left", "down", "down"],                     # EXO-45 Patriot Exosuit
    "HD2-FRV": ["left", "down", "right", "down", "right", "down", "up"],                    # M-102 Fast Recon Vehicle
    "HD2-BAS": ["left", "down", "right", "down", "left", "down", "up", "down", "up"],       # TD-220 Bastion MK XVI 
    "HD2-EX52": ["left", "down", "right", "left", "right", "down", "up"],                   # EXO-55 Breakthrough Exosuit 
    "HD2-EX51": ["left", "down", "right", "up", "right", "left", "up"],                     # EXO-51 Lumberer Exosuit 
    
    # == MISSION SPECIFIC ==
    # Ship
    "HD2-Super Destroyer": ["up", "up", "down", "down", "left", "right", "left", "right"],  # Call In Super Destroyer
    "HD2-ERA": ["up", "up", "left", "up", "right"],                                         # Eagle Rearm
    "HD2-Reinforcement": ["up", "down", "right", "left", "up"],                             # Reinforce
    "HD2-Resupply": ["down", "down", "up", "right"],                                        # Resupply
    "HD2-SOS": ["up", "down", "right", "up"],                                               # SOS Beacon
    
    # Objective
                                                                                            # Cargo Container
                                                                                            # Dark Fluid Vessel
    "HD2-Hellbomb": ["down", "up", "left", "down", "up", "right", "down", "up"],            # NUX-223 Hellbomb
    "HD2-SEAF-ALT": ["right", "up", "up", "down"],                                          # SEAF Artillery
    "HD2-SEAF": ["right", "up", "up", "down"],                                              # SEAF Artillery
    "HD2-Seismic Probe": ["up", "up", "left", "right", "down", "down"],                     # Seismic Probe
    "HD2-SEF": ["down", "up", "down", "up"],                                                # Super Earth Flag
                                                                                            # Tectonic Drill
    "HD2-Upload": ["left", "right", "up", "up", "up"],                                      # Upload Data
                                                                                            # Hive Breaker Drill
                                                                                            # Reinforcement Pods
                                                                                            # SSSD Delivery
    "HD2-Prospecting Drill": ["down", "down", "left", "right", "down", "down"],             # Prospecting Drill
    
    # Other
    "HD2-Orbital Illumination Flare": ["right", "right", "left", "left"],                   # Orbital Illumination Flare 
}

SLOT_COORDINATES = [
    {"x1": 112, "y1": 1677, "x2": 267, "y2": 1832},  # Slot 1
    {"x1": 281, "y1": 1677, "x2": 437, "y2": 1832},  # Slot 2
    {"x1": 452, "y1": 1677, "x2": 607, "y2": 1832},  # Slot 3
    {"x1": 621, "y1": 1677, "x2": 778, "y2": 1832}   # Slot 4
]

# State file to share configuration on-the-fly with PythonScriptDeck buttons
STATE_FILE = "current_loadout.txt"

def update_stream_deck_icons(loadout_list):
    """Saves data arrays and rewrites dynamic assets for PythonScriptDeck maps."""
    with open(STATE_FILE, "w") as f:
        f.write(",".join(loadout_list))
        
    for i, name in enumerate(loadout_list):
        src = f"templates/{name}.png"
        dst = f"active_slot_{i}.png"
        if os.path.exists(src):
            shutil.copy(src, dst)
        else:
            blank = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(dst, blank)
    print("[SYSTEM] Stream Deck interface arrays successfully updated.")

def capture_and_analyze():
    print("\nScanning 4K screen layout configuration...")
    screenshot = np.array(ImageGrab.grab())
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

    detected = []
    high_confidence_count = 0  
    
    print("\n--- INDIVIDUAL SLOT CONFIDENCE LOGS ---")
    for i, slot in enumerate(SLOT_COORDINATES):
        crop = screenshot_gray[slot["y1"]:slot["y2"], slot["x1"]:slot["x2"]]
        ch, cw = crop.shape
        cy, cx = int(ch * 0.15), int(cw * 0.15)
        crop_core = crop[cy:ch-cy, cx:cw-cx]
        crop_blur = cv2.GaussianBlur(crop_core, (5, 5), 0)
        
        best_match = "unknown"
        highest_score = 0.0
        
        for name in STRATAGEMS.keys():
            template = cv2.imread(f"templates/{name}.png", cv2.IMREAD_GRAYSCALE)
            if template is None: continue
            
            th, tw = template.shape
            ty, tx = int(th * 0.15), int(tw * 0.15)
            template_core = template[ty:th-ty, tx:tw-tx]
            template_blur = cv2.GaussianBlur(template_core, (5, 5), 0)
            
            for scale in [0.7, 0.8, 0.9, 1.0, 1.1]:
                target_w = int(crop_blur.shape[1] * scale)
                target_h = int(crop_blur.shape[0] * scale)
                resized_temp = cv2.resize(template_blur, (target_w, target_h), interpolation=cv2.INTER_AREA)
                
                if scale <= 1.0:
                    res = cv2.matchTemplate(crop_blur, resized_temp, cv2.TM_CCOEFF_NORMED)
                else:
                    res = cv2.matchTemplate(resized_temp, crop_blur, cv2.TM_CCOEFF_NORMED)
                    
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > highest_score:
                    highest_score = max_val
                    best_match = name
                        
        if highest_score > 0.70:
            detected.append(best_match)
            high_confidence_count += 1
            print(f"Slot {i+1}: {best_match} (Confidence: {highest_score:.2f}) [MATCH]")
        else:
            detected.append("unknown")
            print(f"Slot {i+1}: unknown (Best guess: {best_match} @ {highest_score:.2f}) [REJECTED]")

    print(f"\n[DEBUG] Scan complete. Found {high_confidence_count}/4 recognizable stratagems.")

    # MISCLICK PROTECTION CRITERIA
    if high_confidence_count < 2:
        print("[MISCLICK DETECTED] Low matching signature layout threshold. Aborting profile rewrite to preserve current loadout.")
        return

    print(f"[SUCCESS] Validation passed! Scanned items resolved: {detected}")
    update_stream_deck_icons(detected)

# --- ONE-SHOT EXECUTION MAIN THREAD ---
if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        capture_and_analyze()
    except Exception as e:
        print(f"[CRASH] Core runtime analyzer failed: {e}")
    finally:
        print("[FINISHED] One-shot cycle finished execution context.")