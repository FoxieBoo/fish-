# 🐟 VRChat Auto Fish

Automated fishing bot for VRChat's **FISH!** world. Supports YOLO object detection + PD controller for fully automated casting, hooking, and minigame control.

## Features

- **Auto cast / hook** — Detects bite animation, auto-completes fishing flow
- **Minigame auto-control** — PD controller tracks fish position, controls the white bar
- **YOLO object detection** — Train for higher accuracy (replaces template matching)
- **GUI interface** — Visual parameter tuning, real-time debug window
- **Hotkey control** — F9 start/pause, F10 stop, F11 debug mode
- **VRChat OSC input** — Optional OSC mode, doesn't use your mouse
- **Fast Lock mode** — Aggressive correction for erratic jumping fish
- **Imitation Learning** — Record your gameplay, train a model to replace PD controller

## Quick Start

1. Install [Python 3.10+](https://www.python.org/downloads/) (check "Add to PATH")
2. Run `install.bat` or install manually:

```bash
# GPU version (NVIDIA)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# CPU version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Other dependencies
pip install -r requirements.txt
```

3. Launch: `python main.py`

## Usage

1. Start VRChat and enter the FISH! world
2. Run the program, click **Select Window** to bind VRChat
3. Click **Select Region** to choose the minigame detection area (optional)
4. Press **F9** to start auto fishing

| Key | Function |
|-----|----------|
| F9 | Start / Pause |
| F10 | Stop |
| F11 | Debug Mode (shows detection window) |

## YOLO Training (Optional)

For better detection accuracy, you can train your own YOLO model:

### 1. Collect Screenshots
```bash
python -m yolo.collect           # Default 2 FPS
python -m yolo.collect --fps 4   # 4 FPS (more data)
python -m yolo.collect --max 500 # Stop after 500 screenshots
```

### 2. Label Data
```bash
python -m yolo.label             # Label new images
python -m yolo.label --split 0.2 # 20% to validation set
```

Labeling controls:
| Key | Function |
|-----|----------|
| Mouse drag | Draw box |
| 1 | Select class: fish |
| 2 | Select class: bar |
| 3 | Select class: track |
| 4 | Select class: progress |
| Z | Undo last box |
| S / Enter | Save & next |
| D | Skip image |
| Q / Esc | Quit |

### 3. Train Model
```bash
python -m yolo.train              # Default YOLOv8n, 50 epochs
python -m yolo.train --epochs 100 # Train 100 epochs
python -m yolo.train --resume     # Resume from checkpoint
```

Best model saves to `yolo/runs/fish_detect/weights/best.pt`, auto-loaded on startup.

## Project Structure

```
├── main.py              # Entry point
├── config.py            # Global configuration
├── core/                # Core logic
│   ├── bot.py           # Fishing main loop + PD controller
│   ├── detector.py      # Template matching detection
│   ├── yolo_detector.py # YOLO detection
│   ├── screen.py        # Screen capture
│   ├── window.py        # Window management
│   ├── input_ctrl.py    # Input control (PostMessage + OSC)
│   └── overlay.py       # Debug overlay
├── gui/                 # GUI interface
│   └── app.py
├── utils/               # Utilities
│   └── logger.py
├── img/                 # Template images
├── yolo/                # YOLO model & training tools
├── imitation/           # Imitation learning
├── install.bat          # Install dependencies
└── start.bat            # Launch program
```

## License

MIT
