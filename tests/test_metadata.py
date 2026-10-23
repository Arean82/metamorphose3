"""Tests for metadata extraction through upstream mutagen and exifread."""

import os
import shutil
import sys
import tempfile
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import gettext

gettext.install("metamorphose3", "/nonexistent")

try:
    import exifread
except ImportError:  # pragma: no cover - dependency missing
    exifread = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover - dependency missing
    Image = None

try:
    from mutagen.apev2 import APEv2File
    from mutagen.asf import ASF
    from mutagen.easyid3 import EasyID3
    from mutagen.easymp4 import EasyMP4
    from mutagen.flac import FLAC
    from mutagen.id3 import ID3FileType
    from mutagen.monkeysaudio import MonkeysAudio
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.musepack import Musepack
    from mutagen.oggflac import OggFLAC
    from mutagen.oggspeex import OggSpeex
    from mutagen.oggtheora import OggTheora
    from mutagen.oggvorbis import OggVorbis
    from mutagen.optimfrog import OptimFROG
    from mutagen.trueaudio import TrueAudio
    from mutagen.wavpack import WavPack
    MUTAGEN_IMPORTS = True
except ImportError:  # pragma: no cover - dependency missing
    MUTAGEN_IMPORTS = False

# Same kind list the audio parser probes, in the same order.
AUDIO_KINDS = []
if MUTAGEN_IMPORTS:
    AUDIO_KINDS = [
        MP3, TrueAudio, OggTheora, OggSpeex, OggVorbis, OggFLAC, FLAC,
        APEv2File, EasyMP4, ID3FileType, WavPack, Musepack, MonkeysAudio,
        OptimFROG, ASF,
    ]

# Minimal file that scores as MPEG audio: an ID3 header followed by a frame.
MP3_BYTES = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\xff\xfb\x90\x00" + b"\x00" * 400


class TempDirMixin:
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def path(self, name):
        return os.path.join(self.root, name)


@unittest.skipIf(exifread is None or Image is None, "exifread or Pillow not installed")
class ExifTests(TempDirMixin, unittest.TestCase):
    def _jpeg(self, name="image.jpg"):
        target = self.path(name)
        image = Image.new("RGB", (16, 16), (10, 20, 30))
        exif = Image.Exif()
        exif[0x010F] = "TestMake"
        exif[0x0110] = "TestModel"
        exif[0x0132] = "2026:10:23 15:00:00"
        image.save(target, "JPEG", exif=exif.tobytes())
        return target

    def test_reads_make_and_model(self):
        with open(self._jpeg(), "rb") as handle:
            tags = exifread.process_file(handle, details=False)
        self.assertEqual(str(tags["Image Make"]), "TestMake")
        self.assertEqual(str(tags["Image Model"]), "TestModel")

    def test_reads_datetime(self):
        with open(self._jpeg(), "rb") as handle:
            tags = exifread.process_file(handle, details=False)
        self.assertEqual(str(tags["Image DateTime"]), "2026:10:23 15:00:00")

    def test_reads_tiff(self):
        target = self.path("image.tiff")
        Image.new("RGB", (16, 16), (1, 2, 3)).save(target, "TIFF")
        with open(target, "rb") as handle:
            tags = exifread.process_file(handle, details=False)
        self.assertGreater(len(tags), 0)

    def test_jpeg_without_exif_has_no_image_tags(self):
        target = self.path("plain.jpg")
        Image.new("RGB", (16, 16), (1, 2, 3)).save(target, "JPEG")
        with open(target, "rb") as handle:
            tags = exifread.process_file(handle, details=False)
        self.assertNotIn("Image Make", tags)


@unittest.skipUnless(MUTAGEN_IMPORTS, "mutagen not installed")
class AudioDetectionTests(TempDirMixin, unittest.TestCase):
    def _mp3(self):
        target = self.path("song.mp3")
        with open(target, "wb") as handle:
            handle.write(MP3_BYTES)
        return target

    def test_every_kind_offers_score(self):
        for kind in AUDIO_KINDS:
            with self.subTest(kind=kind.__name__):
                self.assertTrue(hasattr(kind, "score"))

    def test_mp3_is_detected(self):
        filename = self._mp3()
        with open(filename, "rb") as handle:
            header = handle.read(128)
            results = [(kind.score(filename, handle, header), kind.__name__)
                       for kind in AUDIO_KINDS]
        results = list(zip(results, AUDIO_KINDS))
        results.sort()
        (score, name), kind = results[-1]
        self.assertGreater(score, 0)
        self.assertEqual(kind.__name__, "MP3")

    def test_tag_round_trip(self):
        filename = self._mp3()
        tags = EasyID3(filename)
        tags["title"] = ["Track One"]
        tags["artist"] = ["Someone"]
        tags.save()
        reread = EasyID3(filename)
        self.assertEqual(reread["title"][0], "Track One")
        self.assertEqual(reread["artist"][0], "Someone")

    def test_filename_attribute_survives(self):
        filename = self._mp3()
        self.assertEqual(EasyID3(filename).filename, filename)

    def test_unknown_file_scores_zero(self):
        target = self.path("noise.bin")
        with open(target, "wb") as handle:
            handle.write(b"\x00" * 256)
        with open(target, "rb") as handle:
            header = handle.read(128)
            scores = [kind.score(target, handle, header) for kind in AUDIO_KINDS]
        self.assertTrue(all(score <= 0 for score in scores))


if __name__ == "__main__":
    unittest.main()
