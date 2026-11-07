# Plant gate assets

`mobilenet_plant_gate.pt` — MobileNetV3-Small binary classifier (plant vs non-plant), fp16 state_dict.

- Trained on ~700 plant leaf images (from cleaned disease dataset) + ~700 non-plant images.
- Val accuracy ≈ 0.99; default threshold 0.57 (override with `PLANT_GATE_THRESHOLD`).
- Deploy path on the 1.6GB ECS: `backend/ai/plant_gate_assets/mobilenet_plant_gate.pt`.
- Do **not** load full CLIP ViT-B/32 on that host (OOM). This gate adds ~15MB RSS when YOLO/torch is already loaded.

The weight file is kept out of git by default (binary). Copy from the production host or rebuild with the training script used in the gate rollout.

YOLOv8-cls v3 adds its own non-plant class (`other`, YOLO index 1, display name 「非植物/无关图片」). After this gate, a top-1 of that class is returned as `reason=other_class` instead of a disease name. Keep this MobileNet gate. Do not load CLIP.
