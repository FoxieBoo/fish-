"""
行为克隆控制模型
================
轻量 MLP: 最近 N 帧特征 → 按住概率

特征 (每帧 10 维):
  0  error         = bar_cy - fish_cy     (正=白条在鱼下方)
  1  velocity      = 白条速度估算          (正=下落, 负=上升)
  2  bar_h         = 白条高度
  3  fish_delta    = 鱼本帧位移            (正=下移, 负=上移)
  4  dist_ratio    = error / bar_h        (归一化误差)
  5  mouse         = 上一帧是否按住        (0/1)
  6  fish_in_bar   = 鱼在白条内的位置      (0=顶, 0.5=中心, 1=底)
  7  press_streak  = 连续按住/松开帧数     (归一化)
  8  predicted     = error + velocity*0.15 (惯性预测: 150ms后白条相对鱼的位置)
  9  bar_accel     = 速度变化量            (加速度, 正=加速下落)
"""

import torch
import torch.nn as nn


class FishPolicy(nn.Module):
    FEATURES_PER_FRAME = 10

    def __init__(self, history_len: int = 10):
        super().__init__()
        inp = history_len * self.FEATURES_PER_FRAME
        self.net = nn.Sequential(
            nn.Linear(inp, 256),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)

    def predict(self, x: torch.Tensor) -> float:
        """推理: 返回按住概率 [0, 1]"""
        with torch.no_grad():
            return torch.sigmoid(self.forward(x)).item()
