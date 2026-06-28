import sys
import os

# Import our master macro function from press_slot.py
from press_slot import fire_macro

if __name__ == "__main__":
    # Force pass slot index 0
    fire_macro(1)

    sys.__stdout__.write("1")