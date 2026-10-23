# -*- coding: utf-8 -*-
"""
Sidecar companion file detection and synchronisation.
Pairs sidecar metadata files (.xmp, .srt, .sub, .nfo, .thm) with their base media files.
"""

import os

SIDECAR_EXTENSIONS = (
    '.xmp',
    '.srt',
    '.sub',
    '.idx',
    '.nfo',
    '.thm',
    '.info.json',
)


def find_sidecars(base_filepath):
    """
    Given a base file path, find all existing sidecar companion files in the same directory.
    Returns list of matching companion file paths.
    """
    base_dir, base_name = os.path.split(base_filepath)
    stem, _ = os.path.splitext(base_name)
    sidecars = []
    if not os.path.isdir(base_dir):
        return sidecars

    for ext in SIDECAR_EXTENSIONS:
        candidate = os.path.join(base_dir, stem + ext)
        if os.path.exists(candidate) and candidate != base_filepath:
            sidecars.append(candidate)
    return sidecars


def get_sidecar_new_name(base_new_name, sidecar_path):
    """
    Compute the corresponding renamed path for a sidecar based on the base file's new name.
    """
    sidecar_dir, sidecar_file = os.path.split(sidecar_path)
    base_stem, _ = os.path.splitext(os.path.basename(base_new_name))
    for ext in SIDECAR_EXTENSIONS:
        if sidecar_file.lower().endswith(ext):
            return os.path.join(os.path.dirname(base_new_name), base_stem + ext)
    # Default fallback
    sidecar_ext = os.path.splitext(sidecar_file)[1]
    return os.path.join(os.path.dirname(base_new_name), base_stem + sidecar_ext)
