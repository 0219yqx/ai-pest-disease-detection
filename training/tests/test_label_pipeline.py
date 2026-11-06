# -*- coding: utf-8 -*-
"""清洗 → 类别文件 → 部署文件名对齐。不下载数据，也不加载 best.pt。"""

import json
import tempfile
import unittest
from pathlib import Path

from backend.ai.class_names import (
    describe_issues,
    is_dense,
    load_class_names,
    normalize_healthy,
    resolve_label,
)
from training.check_class_names import main as check_main
from training.dataset_layout import PipelineError, deploy_files, needs_clean
from training.fix_dataset_labels import decode_filename, main as fix_main
from training.pipeline import ensure_cleaned
from training.train_yolov8 import build_parser
from training.validate_cls import format_report, read_topk, summarize_confusion

ROOT = Path(__file__).resolve().parents[2]


def _touch(folder: Path, name: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_bytes(b"img")


class DecodeTests(unittest.TestCase):
    def test_codes_and_healthy(self):
        self.assertEqual(decode_filename("Corn___C.Rust 1.jpg")[:2], ("pv_ok", "C.Rust"))
        self.assertEqual(decode_filename("x___HLB 1.jpg")[:2], ("pv_ok", "HLB"))
        self.assertEqual(decode_filename("x___HL 1.jpg")[:2], ("pv_hl", "HL"))
        self.assertEqual(decode_filename("x___Bact.Sp 1.jpg")[1], "Bact.Sp")
        self.assertEqual(decode_filename("00112233445566778899aabbccddeeff.jpg")[0], "md5")
        self.assertEqual(decode_filename("IMG_001.jpg")[0], "other")

    def test_normalize_healthy_suffix_only(self):
        self.assertEqual(normalize_healthy("玉米健康_2"), "玉米健康")
        self.assertEqual(normalize_healthy("番茄健康_12"), "番茄健康")
        self.assertEqual(normalize_healthy("番茄健康_早期"), "番茄健康_早期")
        self.assertEqual(normalize_healthy("玉米锈病"), "玉米锈病")


class ResolveTests(unittest.TestCase):
    def test_legacy_checkpoint_uses_folder_id_not_model_index(self):
        mapping = load_class_names(ROOT / "models" / "class_names.json")
        self.assertFalse(is_dense(mapping))
        self.assertEqual(mapping[75], "马铃薯早疫病")
        self.assertEqual(mapping[10], "水稻褐斑病_轻")
        self.assertEqual(mapping[2], "樱桃白粉病_严重")
        # best.pt 里 class_10 的模型下标是 2，不能显示成下标 2 的病名。
        self.assertEqual(resolve_label(2, "class_10", mapping), "水稻褐斑病_轻")
        self.assertNotEqual(resolve_label(2, "class_10", mapping), mapping[2])
        # 后端已经解析成中文时，不要再用模型下标覆盖。
        self.assertEqual(resolve_label(2, "水稻褐斑病_轻", mapping), "水稻褐斑病_轻")
        issues = "\n".join(describe_issues(mapping))
        self.assertIn("61-74", issues)
        self.assertIn("玉米健康", issues)
        self.assertIn("玉米健康_2", issues)

    def test_dense_map_uses_index_even_if_name_is_class_n(self):
        mapping = {0: "苹果黑星病", 1: "玉米锈病", 2: "葡萄黑腐病"}
        self.assertTrue(is_dense(mapping))
        self.assertEqual(resolve_label(2, "class_10", mapping), "葡萄黑腐病")
        self.assertEqual(resolve_label(1, "玉米锈病", mapping), "玉米锈病")
        self.assertEqual(resolve_label(-1, "非农作物", mapping), "非农作物")
        self.assertEqual(describe_issues(mapping), [])

        class _NumpyLike:
            def item(self):
                return 2

        self.assertEqual(resolve_label(_NumpyLike(), "class_10", mapping), "葡萄黑腐病")


class CleanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.train = self.root / "train"
        self.val = self.root / "val"
        self.out = self.root / "cleaned"
        name_map = {
            "4": "玉米叶斑病_轻",
            "9": "玉米健康_2",
            "18": "葡萄健康",
            "45": "番茄健康_3",
        }
        self.name_map = self.root / "names.json"
        self.name_map.write_text(json.dumps(name_map, ensure_ascii=False), encoding="utf-8")

        for index in range(5):
            _touch(self.train / "class_4", f"Corn___C.Rust {index}.jpg")
        _touch(self.train / "class_4", "stay.jpg")
        _touch(self.train / "class_4", "notes.txt")
        _touch(self.val / "class_4", "Corn___C.Rust 9.jpg")

        for name in ("a___HL 1.jpg", "b.jpg", "c.jpg"):
            _touch(self.train / "玉米健康", name)
        _touch(self.train / "玉米健康_2", "a___HL 1.jpg")
        _touch(self.train / "玉米健康_2", "e.jpg")
        _touch(self.val / "玉米健康", "v___HL 1.jpg")

        for index in range(5):
            _touch(self.train / "玉米锈病", f"already___C.Rust {index}.jpg")

        for index in range(6):
            _touch(self.train / "class_18", f"Grape___B.Rot {index}.jpg")

        _touch(self.train / "class_45", "only.jpg")
        _touch(self.train / "苹果赤霉病", "one.jpg")
        _touch(self.train / "苹果赤霉病", "two.jpg")
        _touch(self.val / "苹果赤霉病", "v.jpg")
        self.source_count = sum(1 for _ in self.train.rglob("*") if _.is_file())

    def tearDown(self):
        self.tmp.cleanup()

    def _apply(self, extra=None):
        argv = [
            "--train", str(self.train),
            "--val", str(self.val),
            "--out", str(self.out),
            "--name-map", str(self.name_map),
            "--min-per-class", "5",
            "--apply",
        ]
        if extra:
            argv.extend(extra)
        fix_main(argv)

    def test_apply_merges_drops_and_writes_dense_names(self):
        self._apply()
        names = json.loads((self.out / "class_names.json").read_text(encoding="utf-8"))
        folders = sorted(path.name for path in (self.out / "train").iterdir() if path.is_dir())
        self.assertEqual(list(names.values()), folders)
        self.assertEqual(list(names.keys()), [str(i) for i in range(len(folders))])
        self.assertEqual(folders, ["玉米健康", "玉米锈病", "葡萄黑腐病"])
        self.assertFalse((self.out / "train" / "玉米健康_2").exists())
        self.assertFalse((self.out / "train" / "苹果赤霉病").exists())
        self.assertFalse((self.out / "train" / "番茄健康").exists())
        self.assertFalse((self.out / "train" / "玉米叶斑病_轻").exists())
        self.assertEqual(len(list((self.out / "train" / "玉米健康").glob("*.jpg"))), 5)
        dup = list((self.out / "train" / "玉米健康").glob("*__dup*.jpg"))
        self.assertEqual(len(dup), 1)
        self.assertFalse((self.out / "train" / "玉米健康" / "notes.txt").exists())
        # 原始目录还在，notes.txt 也还在。
        self.assertTrue((self.train / "class_4" / "notes.txt").is_file())
        self.assertEqual(sum(1 for _ in self.train.rglob("*") if _.is_file()), self.source_count)

        report = (self.out / "audit_report.md").read_text(encoding="utf-8")
        self.assertIn("确证错标", report)
        self.assertIn("玉米健康_2", report)
        self.assertIn("苹果赤霉病: 训练+验证共 3 张，少于 5", report)

        clean, reason = needs_clean(self.out)
        self.assertFalse(clean, reason)
        self.assertEqual(describe_issues(load_class_names(self.out / "class_names.json")), [])

    def test_audit_does_not_copy_and_counts_only_conflicts(self):
        report_path = self.root / "audit.md"
        fix_main([
            "--train", str(self.train),
            "--val", str(self.val),
            "--name-map", str(self.name_map),
            "--report", str(report_path),
        ])
        text = report_path.read_text(encoding="utf-8")
        self.assertIn("仅审计", text)
        self.assertFalse((self.out / "train").exists())
        # 已经在「玉米锈病」里的 5 张不算错标；class_4 的 5 张加 val 的 1 张、以及 class_18 的 6 张算错标。
        self.assertIn("确证且已经在正确类别: 5", text)
        self.assertIn("确证错标（解码病害 ≠ 文件夹规划标签）: 12", text)

    def test_apply_refuses_overlap_and_second_write(self):
        with self.assertRaises(SystemExit):
            fix_main([
                "--train", str(self.train),
                "--val", str(self.val),
                "--out", str(self.train / "nested"),
                "--apply",
            ])
        self.assertFalse((self.train / "nested").exists())
        self._apply()
        with self.assertRaises(SystemExit):
            self._apply()
        self._apply(["--force"])
        self.assertTrue((self.out / "class_names.json").is_file())


class DeployAndMetricsTests(unittest.TestCase):
    def test_shipped_map_is_not_strict(self):
        with self.assertRaises(SystemExit) as raised:
            check_main(["--class-names", str(ROOT / "models" / "class_names.json"), "--strict"])
        self.assertEqual(raised.exception.code, 1)
        check_main(["--class-names", str(ROOT / "models" / "class_names.json")])

    def test_deploy_rejects_legacy_map_and_accepts_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            train = root / "data" / "train"
            _touch(train / "玉米锈病", "a.jpg")
            _touch(train / "葡萄黑腐病", "b.jpg")
            (root / "data" / "val" / "玉米锈病").mkdir(parents=True)
            (root / "data" / "val" / "葡萄黑腐病").mkdir(parents=True)
            from backend.ai.class_names import mapping_from_train, write_class_names
            write_class_names(root / "data" / "class_names.json", mapping_from_train(train))
            weights = root / "best.pt"
            weights.write_bytes(b"not-a-real-model")
            dest = root / "models"
            deploy_files(weights, root / "data" / "class_names.json", dest, train_dir=train)
            self.assertEqual((dest / "best.pt").read_bytes(), b"not-a-real-model")
            self.assertEqual(
                json.loads((dest / "class_names.json").read_text(encoding="utf-8")),
                {"0": "玉米锈病", "1": "葡萄黑腐病"},
            )
            with self.assertRaises(PipelineError):
                deploy_files(weights, ROOT / "models" / "class_names.json", root / "bad", train_dir=train)

    def test_missing_raw_dataset_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = type("Args", (), {})()
            args.data = str(Path(tmp) / "cleaned")
            args.force_clean = False
            args.raw_train = str(Path(tmp) / "no-train")
            args.raw_val = str(Path(tmp) / "no-val")
            args.name_map = str(ROOT / "models" / "class_names.json")
            args.min_per_class = 5
            with self.assertRaises(PipelineError) as raised:
                ensure_cleaned(args)
            self.assertIn("RAW_TRAIN", str(raised.exception))
            self.assertIn("不存在", str(raised.exception))

    def test_confusion_summary_and_defaults(self):
        matrix = [
            [4, 1],
            [0, 2],
        ]
        text = summarize_confusion(matrix, ["玉米锈病", "葡萄黑腐病"])
        self.assertIn("玉米锈病: 召回 0.800（4/5）", text)
        self.assertIn("玉米锈病 → 葡萄黑腐病: 1", text)
        self.assertIn("跳过逐类摘要", summarize_confusion([[1, 0, 0]], ["只有一个"]))
        report = format_report(0.5, None, matrix, ["玉米锈病", "葡萄黑腐病"])
        self.assertIn("top1: 0.5000", report)
        self.assertIn("未能从 ultralytics 结果中读取", report)
        self.assertIn("86.6%", report)

        class Metrics:
            top1 = 0.25
            results_dict = {"metrics/accuracy_top5": 0.75}

        self.assertEqual(read_topk(Metrics()), (0.25, 0.75))
        parser = build_parser()
        args = parser.parse_args(["--data", "somewhere"])
        self.assertEqual(args.model, "yolov8s-cls.pt")
        self.assertEqual(args.imgsz, 384)
        self.assertEqual(args.epochs, 100)
        self.assertEqual(args.patience, 30)


if __name__ == "__main__":
    unittest.main()
