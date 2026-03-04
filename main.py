"""
VRChat Auto Fishing Script — Entry Point
=========================================
Launches the tkinter GUI interface.

Hotkeys (also work inside VRChat):
    F9  = Start / Pause
    F10 = Stop
    F11 = Debug Mode
"""

import tkinter as tk
from gui.app import FishingApp


def main():
    root = tk.Tk()
    FishingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
