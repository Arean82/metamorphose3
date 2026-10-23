"""Tests for media metadata, sidecars, and conflict detection."""

import os
import shutil
import tempfile
import unittest

import sidecar
import video_meta


class SidecarTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_find_and_rename_sidecars(self):
        base_img = os.path.join(self.tmpdir, "photo1.jpg")
        xmp_file = os.path.join(self.tmpdir, "photo1.xmp")
        srt_file = os.path.join(self.tmpdir, "photo1.srt")
        unrelated = os.path.join(self.tmpdir, "other.xmp")

        for p in (base_img, xmp_file, srt_file, unrelated):
            with open(p, "w", encoding="utf-8") as f:
                f.write("content")

        found = sidecar.find_sidecars(base_img)
        self.assertIn(xmp_file, found)
        self.assertIn(srt_file, found)
        self.assertNotIn(unrelated, found)

        new_base = os.path.join(self.tmpdir, "vacation_2024.jpg")
        new_xmp = sidecar.get_sidecar_new_name(new_base, xmp_file)
        self.assertEqual(new_xmp, os.path.join(self.tmpdir, "vacation_2024.xmp"))


class VideoMetadataTests(unittest.TestCase):
    def test_video_metadata_empty_or_parsed(self):
        # Graceful handling of nonexistent or non-video files
        res = video_meta.read_video_metadata("/nonexistent/file.mp4")
        self.assertIsInstance(res, dict)
        self.assertEqual(res, {})


if __name__ == "__main__":
    unittest.main()
