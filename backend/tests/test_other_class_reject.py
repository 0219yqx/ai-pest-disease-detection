"""Pure-function and stub-model checks for the v3 other-class rejection."""
import os
import unittest

os.environ["PLANT_GATE_ENABLED"] = "0"

import numpy as np

from ai.other_class import (
    class_pair_report,
    is_other_class,
    is_other_class_name,
    other_class_reject_result,
)
import ai.predictor as predictor_mod
from ai.predictor import MODEL_CLASSES, Predictor


def _probs(top1, conf, n):
    data = np.full(n, max(1.0 - conf, 0.0) / max(n - 1, 1), dtype=np.float64)
    data[top1] = conf
    data = data / data.sum()
    order = [int(i) for i in np.argsort(-data)[:5]]

    class Probs:
        pass

    probs = Probs()
    probs.top1 = top1
    probs.top1conf = float(data[top1])
    probs.top5 = order
    probs.top5conf = [float(data[i]) for i in order]
    probs.data = data
    return probs


class FakeYOLO:
    def __init__(self, names, probs):
        self.names = names
        self.probs = probs
        self.calls = 0

    def __call__(self, path):
        self.calls += 1

        class Result:
            pass

        result = Result()
        result.probs = self.probs
        return [result]


def _predictor(names, probs):
    predictor = Predictor(model_path="/tmp/yolov8-other-class-missing.pt")
    predictor._model = FakeYOLO(names, probs)
    return predictor


class OtherClassNameTest(unittest.TestCase):
    def test_name_variants(self):
        for label in (
            "other",
            "Other",
            "OTHER",
            "others",
            "non-plant",
            "non_plant",
            "not plant",
            "非植物",
            "无关图片",
            "非植物/无关图片",
            "非植物／无关图片",
            "其他",
            "其它",
        ):
            self.assertTrue(is_other_class_name(label), label)

    def test_real_disease_names_are_not_other(self):
        for label in ("樱桃白粉病", "番茄晚疫病_重", "玉米健康", "未知类别", "class_1", "class_10"):
            self.assertFalse(is_other_class_name(label), label)

    def test_committed_map_index_1_is_a_real_disease(self):
        # The checked-in 64-class map must stay paired with models/best.pt.
        # v3's 「非植物/无关图片」 is deployed with the 67-class weights, not by editing this file alone.
        self.assertEqual(MODEL_CLASSES[1], "樱桃白粉病")
        self.assertFalse(is_other_class_name(MODEL_CLASSES[1]))


class OtherClassDecisionTest(unittest.TestCase):
    def test_label_match_rejects_at_any_index(self):
        self.assertTrue(is_other_class(5, "番茄晚疫病", "非植物/无关图片", {5: "非植物/无关图片"}, 64))
        self.assertTrue(is_other_class(12, "other", "other", None, 64))

    def test_index_1_on_64_class_checkpoint_is_not_enough(self):
        self.assertFalse(
            is_other_class(1, "class_1", "樱桃白粉病", {1: "樱桃白粉病"}, 64)
        )

    def test_v3_index_1_rejects_even_if_json_is_stale(self):
        self.assertTrue(
            is_other_class(1, "class_1", "樱桃白粉病", {1: "樱桃白粉病"}, 67)
        )

    def test_v3_other_index_elsewhere_still_rejects_by_name(self):
        self.assertTrue(is_other_class(40, "other", "小麦锈病", {40: "小麦锈病"}, 67))
        self.assertFalse(is_other_class(0, "class_0", "樱桃健康", {0: "樱桃健康"}, 67))


class OtherClassPayloadTest(unittest.TestCase):
    def test_reject_shape_matches_existing_gate(self):
        payload = other_class_reject_result(1, 0.998, "other", "非植物/无关图片", {1: "非植物/无关图片"}, 67)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["source"], "rejected")
        self.assertEqual(payload["reason"], "other_class")
        self.assertEqual(payload["disease"], "非农作物")
        self.assertEqual(payload["class_id"], -1)
        self.assertFalse(payload["is_confident"])
        self.assertTrue(payload["low_confidence"])
        self.assertIn("非植物", payload["message"])
        self.assertEqual(payload["model_confidence"], 0.998)
        self.assertEqual(payload["other_class_index"], 1)

    def test_non_other_returns_none(self):
        self.assertIsNone(
            other_class_reject_result(1, 0.91, "class_1", "樱桃白粉病", {1: "樱桃白粉病"}, 64)
        )


class ClassPairTest(unittest.TestCase):
    def test_committed_64_class_names_pair_with_class_n_head(self):
        # Alphabetical folder order matches the checkpoint's names dict.
        folders = sorted((f"class_{i}" for i in MODEL_CLASSES), key=str)
        names = {idx: folder for idx, folder in enumerate(folders)}
        report = class_pair_report(names, MODEL_CLASSES)
        self.assertEqual(report["model_nc"], 64)
        self.assertTrue(report["paired"], report["warnings"])
        self.assertFalse(report["v3_other_index_armed"])
        self.assertEqual(names[1], "class_1")

    def test_v3_pair_requires_both_files(self):
        names = {i: f"disease_{i}" for i in range(67)}
        names[1] = "other"
        fresh = {i: f"病害_{i}" for i in range(67)}
        fresh[1] = "非植物/无关图片"
        paired = class_pair_report(names, fresh)
        self.assertTrue(paired["paired"], paired["warnings"])
        self.assertTrue(paired["v3_other_index_armed"])
        self.assertEqual(paired["other_indices"], [1])

        stale = class_pair_report(names, MODEL_CLASSES)
        self.assertFalse(stale["paired"])
        self.assertTrue(any("成对" in warning or "同时替换" in warning or "类别数不一致" in warning for warning in stale["warnings"]))


class PredictorOtherClassTest(unittest.TestCase):
    def test_v3_other_top1_is_rejected_before_success(self):
        names = {i: f"病害_{i}" for i in range(67)}
        names[1] = "other"
        predictor = _predictor(names, _probs(1, 0.997, 67))
        result = predictor.predict("leaf.jpg")
        self.assertEqual(result["source"], "rejected")
        self.assertEqual(result["reason"], "other_class")
        self.assertNotEqual(result["disease"], "非植物/无关图片")
        self.assertNotEqual(result["disease"], "other")
        self.assertEqual(predictor._model.calls, 1)

    def test_64_class_index_1_still_predicts_disease(self):
        folders = sorted((f"class_{i}" for i in MODEL_CLASSES), key=str)
        names = {idx: folder for idx, folder in enumerate(folders)}
        index = next(i for i, name in names.items() if name == "class_1")
        predictor = _predictor(names, _probs(index, 0.93, 64))
        result = predictor.predict("leaf.jpg")
        self.assertEqual(result["source"], "yolov8")
        self.assertEqual(result["disease"], "樱桃白粉病")
        self.assertTrue(result["is_confident"])
        self.assertFalse(result["low_confidence"])

    def test_low_confidence_heuristic_still_rejects(self):
        names = {0: "class_0", 1: "class_1"}
        predictor = _predictor(names, _probs(0, 0.2, 2))
        result = predictor.predict("leaf.jpg")
        self.assertEqual(result["source"], "rejected")
        self.assertEqual(result["reason"], "low_confidence")
        self.assertTrue(result["low_confidence"])
        self.assertTrue(result["message"])

    def test_paired_v3_map_is_the_display_name_for_real_classes(self):
        names = {i: f"folder_{i}" for i in range(67)}
        names[1] = "other"
        mapping = {i: f"病害_{i}" for i in range(67)}
        mapping[0] = "番茄晚疫病_轻"
        mapping[1] = "非植物/无关图片"
        original = predictor_mod.MODEL_CLASSES
        predictor_mod.MODEL_CLASSES = mapping
        try:
            disease = _predictor(names, _probs(0, 0.96, 67)).predict("leaf.jpg")
            rejected = _predictor(names, _probs(1, 0.99, 67)).predict("other.jpg")
        finally:
            predictor_mod.MODEL_CLASSES = original
        self.assertEqual(disease["source"], "yolov8")
        self.assertEqual(disease["disease"], "番茄晚疫病_轻")
        self.assertEqual(rejected["source"], "rejected")
        self.assertEqual(rejected["reason"], "other_class")
        self.assertEqual(rejected["other_class_name"], "非植物/无关图片")

    def test_plant_gate_still_runs_before_yolo(self):
        import ai.plant_gate as plant_gate

        names = {i: f"病害_{i}" for i in range(67)}
        names[1] = "other"
        predictor = _predictor(names, _probs(1, 0.99, 67))

        class Gate:
            threshold = 0.57

            def score(self, path):
                return 0.0

        original = plant_gate.get_gate
        plant_gate.get_gate = lambda: Gate()
        try:
            result = predictor.predict("food.jpg")
        finally:
            plant_gate.get_gate = original
        self.assertEqual(result["reason"], "not_plant")
        self.assertEqual(result["source"], "rejected")
        self.assertEqual(predictor._model.calls, 0)


if __name__ == "__main__":
    unittest.main()
