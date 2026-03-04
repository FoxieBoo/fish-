"""
YOLO 训练数据采集工具
====================
连接 VRChat 窗口，以固定间隔截取钓鱼画面并保存到 dataset/images/unlabeled/。
用户正常钓鱼即可，工具在后台持续截图。

用法:
    python -m yolo.collect            # 每 0.5 秒截一次
    python -m yolo.collect --fps 2    # 每秒截 2 帧
    python -m yolo.collect --roi      # 仅截取 ROI 区域
"""

import os
import sys
import time
import argparse
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.window import WindowManager
from core.screen import ScreenCapture

SAVE_DIR = os.path.join(config.BASE_DIR, "yolo", "dataset", "images", "unlabeled")


def main():
    parser = argparse.ArgumentParser(description="YOLO 钓鱼数据采集")
    parser.add_argument("--fps", type=float, default=2.0,
                        help="每秒截图数 (默认 2)")
    parser.add_argument("--roi", action="store_true",
                        help="仅截取 settings.json 中保存的 ROI 区域")
    parser.add_argument("--max", type=int, default=0,
                        help="最大截图数量 (0 = 无限)")
    args = parser.parse_args()

    os.makedirs(SAVE_DIR, exist_ok=True)

    window = WindowManager(config.WINDOW_TITLE)
    screen = ScreenCapture()

    if not window.find():
        print("[错误] 未找到 VRChat 窗口，请确保游戏正在运行")
        return

    print(f"[✓] 已连接: {window.title} (HWND={window.hwnd})")
    print(f"[设置] 截图间隔: {1/args.fps:.2f}s | ROI: {'是' if args.roi else '否'}")
    print(f"[保存] {SAVE_DIR}")
    print("[提示] 现在开始钓鱼，工具会自动截图。按 Ctrl+C 停止。")
    print()

    roi = None
    if args.roi:
        import json
        try:
            with open(config.SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            roi = data.get("DETECT_ROI")
            if roi:
                print(f"[ROI] X={roi[0]} Y={roi[1]} {roi[2]}x{roi[3]}")
        except Exception:
            pass
        if not roi:
            print("[警告] 未找到保存的 ROI，将截取全屏")

    interval = 1.0 / args.fps
    count = 0

    try:
        while True:
            if not window.is_valid():
                if not window.find():
                    print("[等待] VRChat 窗口未找到，5秒后重试...")
                    time.sleep(5)
                    continue

            img, _ = screen.grab_window(window)
            if img is None:
                time.sleep(0.5)
                continue

            if roi:
                rx, ry, rw, rh = roi
                img = img[ry:ry+rh, rx:rx+rw]

            ts = time.strftime("%Y%m%d_%H%M%S")
            ms = int((time.time() % 1) * 1000)
            filename = f"{ts}_{ms:03d}.png"
            filepath = os.path.join(SAVE_DIR, filename)

            cv2.imwrite(filepath, img)
            count += 1
            h, w = img.shape[:2]
            print(f"  [{count}] {filename} ({w}x{h})", end="\r")

            if args.max > 0 and count >= args.max:
                print(f"\n[完成] 已采集 {count} 张截图")
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n[停止] 共采集 {count} 张截图 → {SAVE_DIR}")


if __name__ == "__main__":
    main()
