"""
YOLO 模型训练脚本
================
用标注好的数据集训练 YOLOv8n 目标检测模型。

用法:
    python -m yolo.train                   # 默认训练
    python -m yolo.train --epochs 100      # 指定轮数
    python -m yolo.train --resume          # 从上次中断处继续训练
    python -m yolo.train --model yolov8s   # 使用更大模型 (精度↑ 速度↓)
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

DATA_YAML = os.path.join(config.BASE_DIR, "yolo", "dataset", "data.yaml")
PROJECT_DIR = os.path.join(config.BASE_DIR, "yolo", "runs")


def count_images(split_dir):
    if not os.path.isdir(split_dir):
        return 0
    return len([f for f in os.listdir(split_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))])


def main():
    parser = argparse.ArgumentParser(description="YOLO 钓鱼模型训练")
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="基础模型 (默认 yolov8n.pt, 可选 yolov8s.pt)")
    parser.add_argument("--epochs", type=int, default=50,
                        help="训练轮数 (默认 50)")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="输入图片尺寸 (默认 640)")
    parser.add_argument("--batch", type=int, default=-1,
                        help="批大小 (-1 = 自动)")
    parser.add_argument("--resume", action="store_true",
                        help="从上次训练中断处继续")
    args = parser.parse_args()

    train_dir = os.path.join(config.BASE_DIR, "yolo", "dataset", "images", "train")
    val_dir = os.path.join(config.BASE_DIR, "yolo", "dataset", "images", "val")
    n_train = count_images(train_dir)
    n_val = count_images(val_dir)

    print("=" * 50)
    print("  VRChat 钓鱼 YOLO 模型训练")
    print("=" * 50)
    print(f"  训练集: {n_train} 张")
    print(f"  验证集: {n_val} 张")
    print(f"  模型:   {args.model}")
    print(f"  轮数:   {args.epochs}")
    print(f"  图片尺寸: {args.imgsz}")
    print(f"  数据配置: {DATA_YAML}")
    print()

    if n_train < 5:
        print("[错误] 训练集图片不足 (至少需要 5 张)")
        print("  请先采集并标注数据:")
        print("    1. python -m yolo.collect    # 采集截图")
        print("    2. python -m yolo.label      # 标注")
        return

    if n_val == 0:
        print("[警告] 验证集为空，建议标注时设置 --split 0.2")
        print()

    try:
        from ultralytics import YOLO
    except ImportError:
        print("[错误] 未安装 ultralytics，请运行:")
        print("  pip install ultralytics")
        return

    if args.resume:
        last_pt = os.path.join(PROJECT_DIR, "fish_detect", "weights", "last.pt")
        if os.path.exists(last_pt):
            print(f"[继续训练] {last_pt}")
            model = YOLO(last_pt)
        else:
            print(f"[警告] 未找到 {last_pt}，从头开始训练")
            model = YOLO(args.model)
    else:
        model = YOLO(args.model)

    import torch
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"[设备] {'GPU: ' + torch.cuda.get_device_name(0) if device == 0 else 'CPU'}")
    if device == "cpu":
        print("[提示] 未检测到 CUDA GPU，将使用 CPU 训练（较慢）")
        print("  安装 GPU 版 PyTorch: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124")

    results = model.train(
        data=DATA_YAML,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=PROJECT_DIR,
        name="fish_detect",
        exist_ok=True,
        device=device,
        workers=4,
        patience=20,
        save=True,
        save_period=10,
        plots=True,
        verbose=True,
    )

    best_pt = os.path.join(PROJECT_DIR, "fish_detect", "weights", "best.pt")
    if os.path.exists(best_pt):
        print()
        print("=" * 50)
        print(f"  [✓] 训练完成！最佳模型: {best_pt}")
        print()
        print(f"  下一步: 在 GUI 中开启 YOLO 模式")
        print(f"  或修改 config.py:")
        print(f'    USE_YOLO = True')
        print(f'    YOLO_MODEL = r"{best_pt}"')
        print("=" * 50)
    else:
        print("[警告] 未找到 best.pt，训练可能未完成")


if __name__ == "__main__":
    main()
