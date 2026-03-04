"""
Global Configuration Module
============================
All tunable parameters managed centrally.
"""

import os
import sys

# ═══════════════════════════════════════════════════════════
#  Paths
# ═══════════════════════════════════════════════════════════
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img")
_APP_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else BASE_DIR
DEBUG_DIR = os.path.join(_APP_DIR, "debug")
SETTINGS_FILE = os.path.join(_APP_DIR, "settings.json")

# ═══════════════════════════════════════════════════════════
#  VRChat Window
# ═══════════════════════════════════════════════════════════
WINDOW_TITLE = "VRChat"

# ═══════════════════════════════════════════════════════════
#  Hotkeys (also work inside VRChat)
# ═══════════════════════════════════════════════════════════
HOTKEY_TOGGLE = "F9"
HOTKEY_STOP   = "F10"
HOTKEY_DEBUG  = "F11"

# ═══════════════════════════════════════════════════════════
#  Timing Parameters (seconds)
# ═══════════════════════════════════════════════════════════
CAST_DELAY          = 1.5         # Wait after casting
BITE_TIMEOUT        = 60.0        # Max wait time for fish (absolute limit)
BITE_FORCE_HOOK     = 18.0        # N sec no bite -> force hook into minigame (prevent missed detection)
BITE_CHECK_INTERVAL = 0.15        # Bite detection interval
MIN_BITE_WAIT       = 3.0         # Min N sec wait before checking for bites (prevent false positives)
COLOR_BITE_WAIT     = 6.0         # Enable color detection after N sec (template matching takes priority)
COLOR_BITE_PIXELS   = 500         # Min pixel count for color detection (higher = stricter)
HOOK_PRE_DELAY      = 0.1         # Delay before hooking
HOOK_POST_DELAY     = 0.4         # Wait for UI to appear after hooking
VERIFY_TIMEOUT      = 3.0         # Timeout for verifying minigame appeared after hooking (sec)
VERIFY_CONSECUTIVE  = 1           # Confirm after N cumulative frames detecting bar+track
GAME_LOOP_INTERVAL  = 0.005       # Minigame loop interval (60FPS game, as fast as possible)
SHOW_DEBUG             = True     # Show debug window (disable for better performance)
DEBUG_OVERLAY_INTERVAL = 0.033    # Debug window min refresh interval (sec) ~30FPS
DEBUG_OVERLAY_MAX_W    = 1920     # Debug window max width (pixels)
DEBUG_OVERLAY_MAX_H    = 1080     # Debug window max height (pixels)
TRACK_LOST_LIMIT    = 60          # N consecutive frames with no fish+bar -> game over
FISH_LOST_LIMIT     = 120         # N consecutive frames fish gone -> game may be over
SINGLE_OBJ_TIMEOUT  = 5.0        # Fish or bar gone alone for N sec -> judge as failed, reel in
OBJ_MIN_COUNT       = 1           # Need at least N objects detected per frame to continue
OBJ_GONE_LIMIT      = 80          # N consecutive frames with insufficient objects -> game over
POST_CATCH_DELAY    = 3.0         # Wait after fishing ends/fails (sec), reel->wait->shake head->cast
SHAKE_HEAD_TIME     = 0.02        # Head shake hold duration per segment (sec)
SHAKE_HEAD_GAP      = 0.05        # Gap between head shake segments (sec)
SHAKE_HEAD_RESET_REPEAT = 2       # Head shake reset repeat count before/after (Left/Right=0)
SHAKE_HEAD_RESET_INTERVAL = 0.01  # Reset resend interval (sec)
INITIAL_PRESS_TIME  = 0.2         # Initial press duration at game start (sec)
SUCCESS_PROGRESS    = 0.55        # Progress bar > this value = fishing success (0~1)
MINIGAME_TIMEOUT    = 120.0       # Minigame max duration (sec), force end if exceeded
UI_CHECK_FRAMES     = 30          # Check if track still exists every N frames
UI_GONE_LIMIT       = 4           # N consecutive track check failures -> game over

# ═══════════════════════════════════════════════════════════
#  Template Matching Confidence Thresholds
#  After ROI selection, search area is very small, low mismatch risk,
#  thresholds can be relaxed significantly.
#    Real fish: 0.61~0.82    Real bar: 0.84~0.89    Real track: 0.51~0.57
# ═══════════════════════════════════════════════════════════
THRESH_BITE     = 0.50
THRESH_FISH     = 0.35           # (lowered for ROI, minimal false matches)
THRESH_BAR      = 0.40           # (lowered for ROI, real values ~0.84+)
THRESH_HOOK     = 0.45
THRESH_TRACK    = 0.35           # (lowered for ROI, no interference)

# ═══════════════════════════════════════════════════════════
#  Multi-scale Matching
# ═══════════════════════════════════════════════════════════
# General scales (track detection)
MATCH_SCALES = [0.7, 1.0, 1.5, 2.0, 3.0]
# Bar scales
BAR_SCALES   = [0.7, 1.0, 1.5, 2.0, 3.0]
# Approximate pixel size of fish icon in game (adjustable in GUI)
# System auto-calculates optimal scale from template size / FISH_GAME_SIZE
# e.g. template 38px, game fish 20px -> optimal scale=1.9, search range 1.1~2.7
FISH_GAME_SIZE = 30

# ═══════════════════════════════════════════════════════════
#  Minigame Control
# ═══════════════════════════════════════════════════════════
# -- PD Controller Parameters (tuned for high-inertia fishing) --
DEAD_ZONE       = 15              # Fixed dead zone (px), fallback (dynamic dead zone takes priority)
DEAD_ZONE_RATIO = 0.35            # Dynamic dead zone: bar height x this ratio (fish within range = centered)
MAINTAIN_TAP_S  = 0.010           # Maintenance tap duration in dead zone (sec), counters gravity
HOLD_MIN_S      = 0.025           # Anti-gravity base (sec) — smaller = falls faster
HOLD_MAX_S      = 0.100           # Max single hold duration (sec)
HOLD_GAIN       = 0.040           # Position gain: error x gain = extra hold duration
VELOCITY_SMOOTH = 0.5             # Velocity low-pass filter coefficient (0~1, higher = smoother)
PREDICT_AHEAD   = 0.5             # Look-ahead time (sec) — high-inertia needs more prediction
SPEED_DAMPING   = 0.00025         # Speed damping: hold longer when falling fast, less when rising
# Fast Lock Mode (for difficult erratic fish)
FAST_LOCK_ENABLED      = True     # More aggressively pull fish back to bar center
FAST_LOCK_JUMP_PX      = 16       # When fish jumps > this many pixels, reduce smoothing lag
FAST_LOCK_SPEED_PX_S   = 700.0    # Fish speed above this triggers fast lock (px/s)
FAST_LOCK_LOOKAHEAD_S  = 0.040    # Fast lock look-ahead time (sec)
FAST_LOCK_TRIGGER_ERR  = 0.15     # Error above this triggers fast lock (normalized by bar height)
FAST_LOCK_BOOST_GAIN   = 0.050    # Fast lock additional press gain
FAST_LOCK_BOOST_MAX_S  = 0.060    # Fast lock max extra hold duration (sec)
FAST_LOCK_DROP_ERR     = 0.28     # Quick release threshold when fish clearly below bar
MAX_FISH_BAR_DIST = 300           # Max reasonable distance between fish and bar center (px)
REGION_UP         = 300           # After bar lock, upward search pixels
REGION_DOWN       = 400           # After bar lock, downward search pixels
REGION_X          = 100           # After bar lock, horizontal search pixels (center +/- N)
USE_OSC           = True          # True=OSC input (doesn't use mouse), False=PostMessage input
DETECT_ROI        = None          # Player-selected detection region [x, y, w, h], None=full screen

# ═══════════════════════════════════════════════════════════
#  YOLO Object Detection (replaces template matching, requires training)
# ═══════════════════════════════════════════════════════════
USE_YOLO      = True
YOLO_MODEL    = os.path.join(BASE_DIR, "yolo", "runs", "fish_detect", "weights", "best.pt")
YOLO_CONF     = 0.45              # YOLO detection confidence threshold
YOLO_DEVICE   = "auto"            # "auto"=prefer GPU / "cpu"=force CPU / "gpu"=force GPU
YOLO_COLLECT  = False             # True=auto-save screenshots during fishing for training
TRACK_MIN_ANGLE   = 3.0           # Track tilt angle threshold (degrees), enable rotation above this
TRACK_MAX_ANGLE   = 45.0          # Track max reasonable angle (degrees), above = false detection

# ═══════════════════════════════════════════════════════════
#  Behavior Cloning (record your actions -> train model -> replace PD controller)
# ═══════════════════════════════════════════════════════════
IL_RECORD       = False           # True=recording mode: detect positions but don't control mouse
IL_USE_MODEL    = False           # True=use trained model for control, False=PD controller
IL_MODEL_PATH   = os.path.join(BASE_DIR, "imitation", "policy.pt")
IL_DATA_DIR     = os.path.join(BASE_DIR, "imitation", "data")
IL_HISTORY_LEN  = 10              # Input history frames (capture fish movement patterns)
IL_PRESS_THRESH = 0.50            # Hold threshold: model probability > this to hold

# ═══════════════════════════════════════════════════════════
#  Template File Mapping
# ═══════════════════════════════════════════════════════════
TEMPLATE_FILES = {
    "track":        "finshblock.png",
    "bar":          "block.png",
    "fish_white":   "wFish.png",
    "fish_green":   "greenFish.png",
    "fish_golden":  "goldenFish.png",
    "fish_copper":  "copperFish.png",
    "fish_blue":    "blueFish.png",
    "fish_purple":  "purpleFish.png",
    "fish_black":   "blackFish.png",
    "hook":         "gou.png",
    "prog_full":    "full.png",
    "prog_empty":   "null.png",
}

# All fish template keys (used by find_fish)
FISH_KEYS = [
    "fish_white", "fish_green", "fish_golden",
    "fish_copper", "fish_blue", "fish_purple", "fish_black",
    "fish_pink", "fish_red", "fish_rainbow",
]

# ═══════════════════════════════════════════════════════════
#  Fish Whitelist (True=catch, False=skip)
# ═══════════════════════════════════════════════════════════
FISH_WHITELIST = {
    "fish_black":   True,   # Black Fish
    "fish_white":   True,   # White Fish
    "fish_copper":  True,   # Copper Fish
    "fish_green":   True,   # Green Fish
    "fish_blue":    True,   # Blue Fish
    "fish_purple":  True,   # Purple Fish
    "fish_pink":    True,   # Pink Fish
    "fish_red":     True,   # Red Fish
    "fish_rainbow": True,   # Rainbow Fish
}
