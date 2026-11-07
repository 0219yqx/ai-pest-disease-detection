# -*- coding: utf-8 -*-
"""Label map, image-level split, and dataset_v4 layout. No dataset download."""

import json
import tempfile
import unittest
from pathlib import Path

from training.v4.prepare_dataset_v4 import main as prepare_main
from training.v4.prepare_dataset_v4 import plan_rows, write_dataset
from training.v4.train_v4 import build_parser
from training.v4.wheat_labels import (
    CATEGORIES,
    OTHER_DISPLAY,
    ZENODO_IMAGE_COUNTS,
    ZENODO_YAML_NAMES,
    assign_image_splits,
    boxes_look_normalized,
    build_class_names,
    other_index,
    padded_rect,
    parse_zenodo_names,
    resolve_split,
    yaml_id_for_category,
)


def _crop(image_id, source_split, yaml_id, digest, payload):
    return {
        "image_id": image_id,
        "source_split": source_split,
        "yaml_id": yaml_id,
        "folder": CATEGORIES[yaml_id]["folder"],
        "digest": digest,
        "filename": f"{image_id}_{digest}.jpg",
        "payload": payload,
    }


class ZenodoMapTest(unittest.TestCase):
    def test_snapshot_is_the_only_source_of_names(self):
        parsed = parse_zenodo_names(ZENODO_YAML_NAMES)
        self.assertEqual(parsed, CATEGORIES)
        self.assertEqual(
            [spec["en"] for spec in CATEGORIES.values()],
            [
                "Powdery Mildew",
                "Scab",
                "Leaf Rust",
                "Stripe Rust",
                "Glume Blotch",
                "Wheat Ear",
                "Wheat Leaf",
            ],
        )
        self.assertEqual(
            [spec["folder"] for spec in CATEGORIES.values()],
            [
                "小麦白粉病",
                "小麦赤霉病",
                "小麦叶锈病",
                "小麦条锈病",
                "小麦颖枯病",
                "小麦正常麦穗",
                "小麦正常麦叶",
            ],
        )

    def test_image_counts_match_the_zip_listing(self):
        self.assertEqual(sum(ZENODO_IMAGE_COUNTS.values()), 4156)
        self.assertTrue(all(n >= 400 for n in ZENODO_IMAGE_COUNTS.values()))

    def test_hf_digit_names_are_yaml_ids(self):
        names = [str(i) for i in range(7)]
        for cid in range(7):
            self.assertEqual(yaml_id_for_category(cid, names), cid)

    def test_hf_english_names_follow_the_string_not_a_guess(self):
        names = [spec["en"] for spec in CATEGORIES.values()]
        self.assertEqual(yaml_id_for_category(4, names), 4)
        with self.assertRaises(KeyError):
            yaml_id_for_category(0, ["not a wheat disease"])

    def test_permuted_digit_names_trust_the_digit(self):
        # Position 0 carries the yaml id written in the name, not the position.
        names = ["4", "0", "1", "2", "3", "5", "6"]
        self.assertEqual(yaml_id_for_category(0, names), 4)


class SplitAndDedupTest(unittest.TestCase):
    def test_crops_from_one_photo_stay_together(self):
        rows = [
            _crop("photo-a", "train", 0, "d1", b"a"),
            _crop("photo-a", "train", 2, "d2", b"b"),
            _crop("photo-a", "test", 4, "d3", b"c"),
            _crop("photo-b", "test", 0, "d1", b"dup"),
            _crop("photo-c", "valid", 4, "d4", b"d"),
        ]
        final, stats = plan_rows(rows, min_crops=1, keep_test=False)
        by_image = {}
        for row in final:
            by_image.setdefault(row["image_id"], set()).add(row["split"])
        self.assertEqual(by_image["photo-a"], {"train"})
        self.assertEqual(len([r for r in final if r["image_id"] == "photo-a"]), 3)
        self.assertNotIn("photo-b", by_image)
        self.assertEqual(by_image["photo-c"], {"val"})
        self.assertEqual(stats["duplicate_crops_dropped"], 1)
        self.assertEqual(stats["images_with_conflicting_splits"], 1)
        self.assertNotIn("test", {row["split"] for row in final})

    def test_keep_test_still_does_not_split_one_photo(self):
        rows = assign_image_splits(
            [
                {"image_id": "p", "source_split": "test"},
                {"image_id": "p", "source_split": "train"},
            ],
            keep_test=True,
        )
        self.assertEqual({row["split"] for row in rows}, {"train"})

    def test_unknown_split_is_refused(self):
        with self.assertRaises(ValueError):
            resolve_split("holdout")

    def test_small_class_is_dropped_not_merged(self):
        rows = [
            _crop("a", "train", 0, "d1", b"a"),
            _crop("b", "train", 0, "d2", b"b"),
            _crop("c", "train", 3, "d3", b"c"),
        ]
        final, stats = plan_rows(rows, min_crops=2, keep_test=False)
        self.assertEqual({row["yaml_id"] for row in final}, {0})
        dropped = stats["dropped_small_classes"]["3"]
        self.assertIn("not merged", dropped["reason"])
        self.assertEqual(dropped["folder"], "小麦条锈病")
        self.assertIn("1", stats["classes_with_no_crops"])


class BoxTest(unittest.TestCase):
    def test_padding_clips_to_the_image(self):
        rect = padded_rect([0, 0, 10, 10], 20, 20, 0.5, normalized=False)
        self.assertEqual(rect, (0, 0, 15, 15))

    def test_normalized_coco_box(self):
        self.assertTrue(boxes_look_normalized([[0.25, 0.25, 0.5, 0.5]]))
        self.assertFalse(boxes_look_normalized([[10, 10, 40, 40]]))
        rect = padded_rect([0.25, 0.25, 0.5, 0.5], 100, 100, 0.0, normalized=True)
        self.assertEqual(rect, (25, 25, 75, 75))

    def test_empty_box_is_skipped(self):
        self.assertIsNone(padded_rect([5, 5, 0, 4], 20, 20, 0.1, normalized=False))


class IndexTest(unittest.TestCase):
    def test_chinese_wheat_folders_do_not_move_other(self):
        wheat = [spec["folder"] for spec in CATEGORIES.values()]
        for prefix in ([], ["class_60"], ["aaa", "mmm"]):
            v3 = prefix + ["other", "苹果健康", "玉米健康"]
            self.assertEqual(other_index(v3), other_index(v3 + wheat))

    def test_v3_contract_index_stays_1_after_wheat_folders(self):
        v3 = ["class_60", "other", "苹果健康"]
        wheat = [spec["folder"] for spec in CATEGORIES.values()]
        folders = v3 + wheat
        self.assertEqual(other_index(v3), 1)
        self.assertEqual(other_index(folders), 1)
        mapping = build_class_names(folders, {})
        self.assertEqual(mapping["1"], OTHER_DISPLAY)
        # 小麦 sorts after ASCII and before 苹果.
        self.assertLess(int([k for k, v in mapping.items() if v == "小麦叶锈病"][0]), int([k for k, v in mapping.items() if v == "苹果健康"][0]))
        self.assertGreater(int([k for k, v in mapping.items() if v == "小麦叶锈病"][0]), 1)

    def test_english_folder_names_would_move_other(self):
        v3 = ["class_60", "other", "苹果健康"]
        moved = other_index(v3 + ["glume_blotch", "leaf_rust"])
        self.assertEqual(moved, 3)


class LayoutTest(unittest.TestCase):
    def test_junction_or_symlink_reuses_v3_and_writes_wheat_crops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v3 = root / "dataset_v3"
            v4 = root / "dataset_v4"
            for split in ("train", "val"):
                for name in ("class_60", "other", "苹果健康"):
                    folder = v3 / split / name
                    folder.mkdir(parents=True)
                    (folder / "keep.txt").write_text(name, encoding="utf-8")
            only_train = v3 / "train" / "玉米健康"
            only_train.mkdir()
            (only_train / "keep.txt").write_text("corn", encoding="utf-8")

            rows = [
                _crop("photo-a", "train", 0, "d1", b"powdery"),
                _crop("photo-a", "test", 2, "d2", b"leaf"),
                _crop("photo-c", "valid", 4, "d4", b"glume"),
            ]
            final, _stats = plan_rows(rows, min_crops=1, keep_test=False)
            # 字母序是 class_60, other, 玉米健康, 苹果健康。json 必须按这个顺序对齐。
            v3_json = {"0": "class_60", "1": "非植物/无关图片", "2": "玉米健康", "3": "苹果健康"}
            report = write_dataset(v3, v4, final, v3_json, keep_test=False)

            self.assertEqual(report["v4_other_index"], 1)
            mapping = json.loads((v4 / "class_names.json").read_text(encoding="utf-8"))
            self.assertEqual(mapping["1"], OTHER_DISPLAY)
            link = v4 / "train" / "other"
            self.assertTrue(link.is_symlink())
            self.assertEqual((link / "keep.txt").read_text(encoding="utf-8"), "other")
            self.assertFalse((v4 / "val" / "玉米健康").is_symlink())
            self.assertFalse((v4 / "val" / "玉米健康" / "keep.txt").exists())
            self.assertTrue((v4 / "train" / "玉米健康").is_symlink())
            self.assertTrue((v4 / "train" / "小麦白粉病" / "photo-a_d1.jpg").is_file())
            self.assertTrue((v4 / "train" / "小麦叶锈病" / "photo-a_d2.jpg").is_file())
            self.assertFalse((v4 / "val" / "小麦叶锈病" / "photo-a_d2.jpg").exists())
            self.assertTrue((v4 / "val" / "小麦颖枯病" / "photo-c_d4.jpg").is_file())
            self.assertFalse((v4 / "test").exists())
            self.assertFalse((v3 / "train" / "小麦白粉病").exists())

            staged = root / "staged.jpg"
            staged.write_bytes(b"from-stage")
            staged_rows, _stats = plan_rows([
                _crop("photo-s", "val", 5, "ds", b"unused"),
            ], min_crops=1, keep_test=False)
            staged_rows[0].pop("payload")
            staged_rows[0]["payload_path"] = str(staged)
            write_dataset(v3, v4, staged_rows, v3_json, keep_test=False)
            self.assertEqual((v4 / "val" / "小麦正常麦穗" / "photo-s_ds.jpg").read_bytes(), b"from-stage")
            self.assertEqual((v3 / "train" / "other" / "keep.txt").read_text(encoding="utf-8"), "other")

            write_dataset(v3, v4, final, v3_json, keep_test=False)
            self.assertEqual((v3 / "train" / "other" / "keep.txt").read_text(encoding="utf-8"), "other")

    def test_refuse_to_write_through_a_v3_folder_of_the_same_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v3 = root / "dataset_v3"
            for split in ("train", "val"):
                for name in ("other", "小麦白粉病"):
                    (v3 / split / name).mkdir(parents=True)
            rows = [_crop("p", "train", 0, "d", b"x")]
            final, _stats = plan_rows(rows, min_crops=1, keep_test=False)
            with self.assertRaises(SystemExit):
                write_dataset(v3, root / "dataset_v4", final, None, keep_test=False)
            self.assertFalse((v3 / "train" / "小麦白粉病" / "p_d.jpg").exists())


class DryRunAndTrainDefaultsTest(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepare_main([
                "--dry-run",
                "--root", str(root),
                "--dataset-v3", str(root / "missing_v3"),
                "--dataset-v4", str(root / "dataset_v4"),
            ])
            self.assertFalse((root / "dataset_v4").exists())

    def test_train_defaults_match_the_v4_recipe(self):
        args = build_parser().parse_args([])
        self.assertEqual(args.imgsz, 384)
        self.assertEqual(args.epochs, 30)
        self.assertEqual(args.batch, 32)
        self.assertEqual(args.workers, 4)
        self.assertEqual(args.patience, 10)
        self.assertTrue(args.amp)
        self.assertEqual(args.name, "plant_disease_v4")

    def test_readme_states_the_other_index(self):
        readme = (Path(__file__).resolve().parent / "README.md").read_text(encoding="utf-8")
        self.assertIn("非植物/无关图片", readme)
        self.assertIn("仍是 index 1", readme)
        self.assertIn("会后移", readme)
        self.assertIn("hf-mirror.com", readme)
        self.assertIn("COPIED", readme)
        self.assertIn("不要提交", readme)
        self.assertIn("10 GB", readme)


if __name__ == "__main__":
    unittest.main()
