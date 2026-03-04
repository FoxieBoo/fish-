"""
YOLO 目标检测器
==============
封装 ultralytics YOLO 推理，提供与模板匹配 Detector 兼容的接口。

检测类别:
  0 = fish     (鱼图标)      → 返回 (x, y, w, h, conf)
  1 = bar      (白色捕捉条)  → 返回 (x, y, w, h, conf)
  2 = track    (钓鱼轨道)    → 返回 (x, y, w, h, conf)
  3 = progress (绿色进度条)  → 返回 (x, y, w, h, conf)
"""

import os
import cv2
import numpy as np
from utils.logger import log

_YOLO_AVAILABLE = False
try:
    from ultralytics import YOLO
    _YOLO_AVAILABLE = True
except ImportError:
    pass


class YoloDetector:
    """YOLO-based fishing game detector."""

    CLASS_FISH = 0
    CLASS_BAR = 1
    CLASS_TRACK = 2
    CLASS_PROGRESS = 3

    def __init__(self, model_path: str, conf: float = 0.5, device="auto"):
        if not _YOLO_AVAILABLE:
            raise ImportError(
                "ultralytics 未安装。请运行: pip install ultralytics"
            )
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"YOLO 模型未找到: {model_path}")

        self.conf = conf
        self.model = YOLO(model_path)

        import config as _cfg
        dev_pref = getattr(_cfg, "YOLO_DEVICE", "auto")
        cuda_ok = False
        try:
            import torch
            cuda_ok = torch.cuda.is_available()
        except Exception:
            pass
        if dev_pref == "cpu" or not cuda_ok:
            target_dev = "cpu"
        elif dev_pref == "gpu":
            target_dev = 0
        else:
            target_dev = 0

        warmup_img = np.zeros((640, 640, 3), dtype=np.uint8)

        if target_dev != "cpu":
            try:
                pass  # 静默加载
                self.model.predict(
                    warmup_img, conf=0.5, device=target_dev,
                    verbose=False, imgsz=640,
                )
                self._device = target_dev
                for _ in range(2):
                    self.model.predict(
                        warmup_img, conf=0.5, device=target_dev,
                        verbose=False, imgsz=640,
                    )
                pass  # GPU 预热完成
                return
            except Exception as e:
                if dev_pref == "gpu":
                    raise RuntimeError(f"[YOLO] 强制 GPU 模式但初始化失败: {e}")
                log.warning(f"[YOLO] GPU 不可用 ({e}), 回退 CPU")

        self._device = "cpu"
        pass  # 静默加载 CPU
        self.model.predict(
            warmup_img, conf=0.5, device="cpu",
            verbose=False, imgsz=640,
        )
        log.info(f"[YOLO] ✓ CPU 模式就绪: {self.model.names}")

    def detect(self, screen, roi=None):
        """
        对一帧画面执行 YOLO 推理。

        参数:
            screen: BGR 图像 (numpy array)
            roi:    [x, y, w, h] 检测区域 (可选)

        返回:
            dict: {
                'fish':  (x, y, w, h, conf) 或 None,
                'bar':   (x, y, w, h, conf) 或 None,
                'track': (x, y, w, h, conf) 或 None,
                'fish_name': str,  # 鱼的类别名称
                'raw': list,       # 所有检测结果
            }
        """
        ox, oy = 0, 0
        img = screen

        if roi:
            rx, ry, rw, rh = roi
            h_s, w_s = screen.shape[:2]
            rx = max(0, min(rx, w_s))
            ry = max(0, min(ry, h_s))
            rw = min(rw, w_s - rx)
            rh = min(rh, h_s - ry)
            if rw > 10 and rh > 10:
                img = screen[ry:ry+rh, rx:rx+rw].copy()
                ox, oy = rx, ry

        results = self.model.predict(
            img, conf=self.conf, device=self._device,
            verbose=False, imgsz=640,
        )

        detections = {
            "fish": None,
            "bar": None,
            "track": None,
            "progress": None,
            "fish_name": "",
            "raw": [],
        }

        if not results or len(results) == 0:
            return detections

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return detections

        for i in range(len(boxes)):
            cls = int(boxes.cls[i])
            conf = float(boxes.conf[i])
            x1, y1, x2, y2 = boxes.xyxy[i].tolist()

            bx = int(x1) + ox
            by = int(y1) + oy
            bw = int(x2 - x1)
            bh = int(y2 - y1)

            det = (bx, by, bw, bh, conf)
            class_name = self.model.names.get(cls, f"cls{cls}")
            detections["raw"].append((class_name, det))

            if class_name == "fish":
                if detections["fish"] is None or conf > detections["fish"][4]:
                    detections["fish"] = det
                    detections["fish_name"] = "fish"
            elif class_name == "bar":
                if detections["bar"] is None or conf > detections["bar"][4]:
                    detections["bar"] = det
            elif class_name == "track":
                if detections["track"] is None or conf > detections["track"][4]:
                    detections["track"] = det
            elif class_name == "progress":
                if detections["progress"] is None or conf > detections["progress"][4]:
                    detections["progress"] = det

        return detections

    def detect_track(self, screen, roi=None):
        """仅检测轨道是否存在"""
        result = self.detect(screen, roi)
        return result["track"]

    def detect_bar(self, screen, roi=None):
        """仅检测白条"""
        result = self.detect(screen, roi)
        return result["bar"]

    def detect_fish(self, screen, roi=None):
        """仅检测鱼"""
        result = self.detect(screen, roi)
        return result["fish"], result["fish_name"]
