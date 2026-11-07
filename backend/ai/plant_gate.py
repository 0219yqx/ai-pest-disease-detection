"""Lightweight plant gate: MobileNetV3-Small binary (plant vs non-plant).

Replaces full CLIP ViT-B/32 (~600MB+) which OOM'd the 1.6GB ECS.
Peak RSS increase is typically ~30–60MB on top of YOLO.
"""
from __future__ import annotations

import os
import threading
from pathlib import Path

PLANT_GATE_THRESHOLD = float(os.getenv("PLANT_GATE_THRESHOLD", "0.57"))
PLANT_GATE_ENABLED = os.getenv("PLANT_GATE_ENABLED", "1") != "0"

_ASSET_DIR = Path(__file__).resolve().parent / "plant_gate_assets"
PLANT_GATE_WEIGHTS = os.getenv(
    "PLANT_GATE_WEIGHTS",
    str(_ASSET_DIR / "mobilenet_plant_gate.pt"),
)
INPUT_SIZE = int(os.getenv("PLANT_GATE_INPUT", "160"))


class PlantGate:
    def __init__(self):
        self.ok = False
        self._lock = threading.Lock()
        self.threshold = PLANT_GATE_THRESHOLD
        self.model = None
        self.preprocess = None
        self.torch = None
        if not PLANT_GATE_ENABLED:
            print("[PlantGate] disabled via PLANT_GATE_ENABLED=0")
            return
        try:
            import torch
            import torch.nn as nn
            from torchvision import models, transforms
            from PIL import Image  # noqa: F401 — ensure available at import time

            weights_path = Path(PLANT_GATE_WEIGHTS)
            if not weights_path.exists():
                raise FileNotFoundError(f"weights missing: {weights_path}")

            ckpt = torch.load(str(weights_path), map_location="cpu", weights_only=False)
            thr = float(ckpt.get("threshold", PLANT_GATE_THRESHOLD))
            # env wins if explicitly set differently from default packaging
            if "PLANT_GATE_THRESHOLD" in os.environ:
                thr = PLANT_GATE_THRESHOLD
            self.threshold = thr

            model = models.mobilenet_v3_small(weights=None)
            model.classifier[3] = nn.Linear(model.classifier[3].in_features, 2)
            sd = ckpt["state_dict"]
            # allow fp16-packaged weights; run inference in float32
            sd = {k: (v.float() if hasattr(v, "float") and v.is_floating_point() else v) for k, v in sd.items()}
            model.load_state_dict(sd)
            model.float().eval()
            for p in model.parameters():
                p.requires_grad_(False)

            self.model = model
            self.torch = torch
            self.preprocess = transforms.Compose(
                [
                    transforms.Resize((INPUT_SIZE, INPUT_SIZE)),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ]
            )
            self.ok = True
            print(
                f"[PlantGate] MobileNetV3-Small loaded thr={self.threshold} "
                f"val_acc={ckpt.get('val_acc')}"
            )
        except Exception as e:
            print(f"[PlantGate] 加载失败，门控关闭: {e}")

    def score(self, image_path):
        """Return plant probability in [0,1]; None if gate unavailable."""
        if not self.ok:
            return None
        from PIL import Image

        torch = self.torch
        img = self.preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0)
        with self._lock, torch.no_grad():
            logits = self.model(img)
            prob = torch.softmax(logits, dim=1)[0, 1]
        return float(prob)


_gate = None


def get_gate():
    global _gate
    if _gate is None:
        _gate = PlantGate()
    return _gate
