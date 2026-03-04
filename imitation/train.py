"""
行为克隆训练脚本
================
读取录制的 CSV 数据 → 训练 MLP → 保存 policy.pt

用法:
    python -m imitation.train
    python -m imitation.train --epochs 200
    python -m imitation.train --lr 0.001
"""

import os
import sys
import io
import csv
import argparse
import random
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

FEATURES_PER_FRAME = 10


def load_sessions(data_dir: str, history_len: int):
    """
    从所有 CSV 文件构建 (X, y) 数据集 — 10维特征。
    所有旧格式 CSV 都能兼容: 缺失的特征从已有列计算。
    """
    csv_files = sorted(
        f for f in os.listdir(data_dir) if f.endswith(".csv")
    )
    if not csv_files:
        print(f"[错误] {data_dir} 中没有找到 CSV 文件")
        print("  请先在 GUI 中启用「录制模式」并手动钓鱼几次")
        sys.exit(1)

    all_X, all_y = [], []
    total_rows = 0

    for fname in csv_files:
        path = os.path.join(data_dir, fname)
        rows = []
        press_streak = 0
        prev_velocity = 0.0

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    mouse = int(row["mouse_pressed"])
                    error = float(row["error"])
                    velocity = float(row["velocity"])
                    bar_h = float(row["bar_h"])
                    fish_delta = float(row["fish_delta"])
                    dist_ratio = float(row["dist_ratio"])

                    # fish_in_bar
                    if "fish_in_bar" in row and row["fish_in_bar"]:
                        fish_in_bar = float(row["fish_in_bar"])
                    else:
                        fish_cy = float(row["fish_cy"])
                        bar_cy = float(row["bar_cy"])
                        bar_top = bar_cy - bar_h / 2
                        fish_in_bar = (fish_cy - bar_top) / max(bar_h, 1)

                    # press_streak
                    if "press_streak" in row and row["press_streak"]:
                        ps = float(row["press_streak"])
                    else:
                        if mouse == 1:
                            press_streak = max(1, press_streak + 1)
                        else:
                            press_streak = min(-1, press_streak - 1)
                        ps = press_streak / 10.0

                    # predicted (惯性预测)
                    if "predicted" in row and row["predicted"]:
                        predicted = float(row["predicted"])
                    else:
                        predicted = error + velocity * 0.15

                    # bar_accel (加速度)
                    if "bar_accel" in row and row["bar_accel"]:
                        bar_accel = float(row["bar_accel"])
                    else:
                        bar_accel = velocity - prev_velocity
                    prev_velocity = velocity

                    mouse_prev = rows[-1][1] if rows else mouse

                    feats = [error, velocity, bar_h, fish_delta,
                             dist_ratio, mouse_prev, fish_in_bar, ps,
                             predicted, bar_accel]
                    rows.append((feats, mouse))
                except (ValueError, KeyError):
                    continue

        total_rows += len(rows)

        for i in range(history_len, len(rows)):
            window = []
            for j in range(i - history_len, i):
                window.extend(rows[j][0])
            all_X.append(window)
            all_y.append(rows[i][1])

        print(f"  ✓ {fname}: {len(rows)} 帧")

    print(f"\n总计: {len(csv_files)} 个录制文件, {total_rows} 帧")
    print(f"训练样本: {len(all_X)} (去掉前 {history_len} 帧作为历史)")
    print(f"每帧特征: {FEATURES_PER_FRAME} 维")

    return np.array(all_X, dtype=np.float32), np.array(all_y, dtype=np.float32)


def main():
    parser = argparse.ArgumentParser(description="行为克隆训练")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--lr", type=float, default=0.0005)
    parser.add_argument("--batch", type=int, default=128)
    parser.add_argument("--val-split", type=float, default=0.15,
                        help="验证集比例")
    args = parser.parse_args()

    print("=" * 50)
    print("  行为克隆训练")
    print("=" * 50)
    print(f"\n加载数据: {config.IL_DATA_DIR}\n")

    X, y = load_sessions(config.IL_DATA_DIR, config.IL_HISTORY_LEN)

    if len(X) < 50:
        print(f"\n[警告] 样本太少 ({len(X)})，建议至少录制 3-5 局钓鱼")
        if len(X) < 10:
            print("[错误] 样本不足 10 个，无法训练")
            sys.exit(1)

    press_ratio = y.mean()
    print(f"按住比例: {press_ratio:.1%} (理想范围 30%~70%)")

    if press_ratio < 0.05 or press_ratio > 0.95:
        print("[警告] 按/松比例严重失衡，可能影响训练效果")

    import torch
    import torch.nn as nn
    from torch.utils.data import TensorDataset, DataLoader
    from imitation.model import FishPolicy

    # ── 特征归一化 (按列 z-score, 保存参数供推理时使用) ──
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std < 1e-6] = 1.0  # 防止除零
    X = (X - mean) / std
    print(f"特征归一化: mean 范围 [{mean.min():.1f}, {mean.max():.1f}], "
          f"std 范围 [{std.min():.2f}, {std.max():.2f}]")

    indices = list(range(len(X)))
    random.shuffle(indices)
    val_n = max(1, int(len(X) * args.val_split))
    val_idx = indices[:val_n]
    train_idx = indices[val_n:]

    X_train = torch.tensor(X[train_idx])
    y_train = torch.tensor(y[train_idx])
    X_val = torch.tensor(X[val_idx])
    y_val = torch.tensor(y[val_idx])

    # 类别权重 (处理不平衡)
    n_pos = y_train.sum().item()
    n_neg = len(y_train) - n_pos
    if n_pos > 0 and n_neg > 0:
        pos_weight = torch.tensor([n_neg / n_pos])
    else:
        pos_weight = torch.tensor([1.0])

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"设备: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    model = FishPolicy(history_len=config.IL_HISTORY_LEN).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr,
                                   weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs
    )

    train_ds = TensorDataset(X_train, y_train)
    train_dl = DataLoader(train_ds, batch_size=args.batch, shuffle=True,
                          drop_last=False)

    X_val_d = X_val.to(device)
    y_val_d = y_val.to(device)

    best_val_acc = 0.0
    best_state = None

    print(f"\n{'Epoch':>6} | {'Train Loss':>10} | {'Val Loss':>8} | "
          f"{'Val Acc':>7} | {'LR':>8}")
    print("-" * 55)

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        for xb, yb in train_dl:
            xb, yb = xb.to(device), yb.to(device)
            logits = model(xb)
            loss = criterion(logits, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(xb)
        avg_loss = total_loss / len(train_ds)
        scheduler.step()

        model.eval()
        with torch.no_grad():
            val_logits = model(X_val_d)
            val_loss = criterion(val_logits, y_val_d).item()
            val_preds = (torch.sigmoid(val_logits) > 0.5).float()
            val_acc = (val_preds == y_val_d).float().mean().item()

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if epoch % 10 == 0 or epoch == 1:
            lr = scheduler.get_last_lr()[0]
            print(f"{epoch:>6} | {avg_loss:>10.4f} | {val_loss:>8.4f} | "
                  f"{val_acc:>6.1%} | {lr:>8.6f}")

    print("-" * 55)
    print(f"最佳验证准确率: {best_val_acc:.1%}")

    os.makedirs(os.path.dirname(config.IL_MODEL_PATH), exist_ok=True)
    save_data = {
        "model_state": best_state,
        "norm_mean": torch.tensor(mean),
        "norm_std": torch.tensor(std),
        "history_len": config.IL_HISTORY_LEN,
    }
    torch.save(save_data, config.IL_MODEL_PATH)
    print(f"\n模型已保存: {config.IL_MODEL_PATH}")
    print(f"\n使用方法:")
    print(f"  1. 在 GUI 中勾选「模型控制」")
    print(f"  2. 或在 config.py 中设置 IL_USE_MODEL = True")


if __name__ == "__main__":
    main()
