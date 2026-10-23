"""Import and configuration invariants for the application package."""

import os
import sys
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import gettext

gettext.install("metamorphose3", "/nonexistent")

APP_MODULES = [
    "app",
    "classes",
    "configs",
    "errors.wxErrorsView",
    "helpDiag",
    "langSelect",
    "operations",
    "operations.accentStrip",
    "operations.changeLength",
    "operations.dateTime",
    "operations.directory",
    "operations.directoryTools",
    "operations.greekNumb",
    "operations.insert",
    "operations.insertTools",
    "operations.modification",
    "operations.move",
    "operations.notebook",
    "operations.numbering",
    "operations.opButtons",
    "operations.opParser",
    "operations.regExpr",
    "operations.replace",
    "operations.replaceTools",
    "operations.roman",
    "operations.search",
    "operations.swap",
    "picker",
    "picker.wxPickerView",
    "preferences",
    "sorting",
    "utils",
]


class ImportTests(unittest.TestCase):
    def test_modules_import(self):
        import importlib

        for name in APP_MODULES:
            with self.subTest(module=name):
                importlib.import_module(name)

    def test_renamer_modules_load_without_app(self):
        # renamer/__init__.py builds widgets at import time and needs a running
        # wx.App, so the pure modules are loaded from their files directly.
        import importlib.util

        for name in ("engine", "preview"):
            with self.subTest(module=name):
                path = os.path.join(SRC, "renamer", name + ".py")
                spec = importlib.util.spec_from_file_location("_probe_" + name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)


class ApplicationInvariants(unittest.TestCase):
    def test_reported_version_is_three(self):
        import app

        self.assertEqual(app.version, "3.0.0")

    def test_preferences_version_matches(self):
        import app

        self.assertEqual(app.prefsVersion, app.version)

    def test_user_data_directory_name(self):
        import app

        self.assertEqual(app.homedir, ".metamorphose3")

    def test_real_path_points_at_sources(self):
        import app

        self.assertTrue(os.path.isdir(app.realPath))
        self.assertTrue(os.path.isfile(os.path.join(app.realPath, "version")))

    def test_locale_path_returns_directory(self):
        import app

        self.assertIsInstance(app.locale_path("en_US"), str)


class ThirdPartyDependencyTests(unittest.TestCase):
    def test_exifread_available(self):
        import exifread

        self.assertTrue(hasattr(exifread, "process_file"))

    def test_mutagen_available(self):
        import mutagen

        self.assertTrue(hasattr(mutagen, "File"))

    def test_pillow_available(self):
        from PIL import Image

        self.assertTrue(hasattr(Image, "open"))

    def test_wxpython_phoenix(self):
        import wx

        self.assertIn("phoenix", wx.version())


if __name__ == "__main__":
    unittest.main()
