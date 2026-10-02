import sys
import os
import time
import ctypes

# --- MACRO RUNTIME LOGGER ---
script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, "macro_log.txt")
sys.stdout = open(log_path, "a", encoding="utf-8", buffering=1)
sys.stderr = sys.stdout


# --- LOW-LEVEL SCANCODE INJECTOR ---
SendInput = ctypes.windll.user32.SendInput

# Hardware Keyboard Scan Codes (Direct Input Architecture)
SCANCODES = {
    "ctrl": 0x1D,
    "numpad8": 0x48,  # Up
    "numpad5": 0x4C,  # Down
    "numpad4": 0x4B,  # Left
    "numpad6": 0x4D   # Right
}

# C struct definitions for low-level Windows API interaction
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra)) # 0x0008 = KEYEVENTF_SCANCODE
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra)) # 0x0002 = KEYEVENTF_KEYUP
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


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


def fire_macro(slot_num):
    state_path = os.path.join(script_dir, "current_loadout.txt")
    print(f"\n[RUN] Triggered Slot {slot_num + 1}")
    
    if not os.path.exists(state_path):
        print(f"[ERROR] missing file context: {state_path}")
        return
        
    with open(state_path, "r") as f:
        loadout = f.read().split(",")
        
    if slot_num >= len(loadout):
        print(f"[ERROR] Slot bound out of range.")
        return
        
    strat = loadout[slot_num]
    print(f"[TARGET] Found stratagem key mapping signature: {strat}")
    
    if strat in STRATAGEMS:
        sequence = STRATAGEMS[strat]
        print(f"[SEQUENCE] Loaded directions: {sequence}")
        
        # Open Menu (Tap Ctrl)
        print(f"[KEY] Sending hardware scancode open -> {STRATAGEM_MENU_KEY}")
        # press_key(SCANCODES[STRATAGEM_MENU_KEY])
        # time.sleep(0.05)
        # release_key(SCANCODES[STRATAGEM_MENU_KEY])
        
        # # UI stabilization delay
        # time.sleep(0.12) 
        
        # Directions loop utilizing raw hardware scan values
        for move in sequence:
            direction_key = ARROW_MAPPING[move]
            hex_code = SCANCODES[direction_key]
            print(f"[KEY] Sending hardware scancode direction: {direction_key} ({hex(hex_code)})")
            
            press_key(hex_code)
            time.sleep(0.05)
            release_key(hex_code)
            time.sleep(0.05)
                
        print("[SUCCESS] Low-level macro execution loop completed.")
    else:
        print(f"[WARNING] Stratagem '{strat}' signature not found in registry maps.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            slot_clicked = int(sys.argv[1])
            fire_macro(slot_clicked)
            sys.__stdout__.write("1")
        except Exception as main_err:
            pass