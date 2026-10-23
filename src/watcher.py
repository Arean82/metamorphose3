# -*- coding: utf-8 -*-
"""
Directory Watcher Daemon for Métamorphose 3.
Monitors an incoming directory for new files and applies batch renaming profiles automatically.
"""

import os
import sys
import time


def watch_directory(target_dir, config_file=None, interval=2.0, callback=None):
    """
    Poll target_dir for new files and invoke rename callback.
    """
    target_dir = os.path.abspath(target_dir)
    if not os.path.isdir(target_dir):
        raise ValueError(f"Directory does not exist: {target_dir}")

    print(f"[Watcher] Started monitoring '{target_dir}' (interval: {interval}s)...")
    seen_files = set(os.listdir(target_dir))

    try:
        while True:
            time.sleep(interval)
            current_files = set(os.listdir(target_dir))
            new_files = current_files - seen_files
            for filename in sorted(new_files):
                full_path = os.path.join(target_dir, filename)
                # Ignore temporary or hidden files
                if filename.startswith('.') or filename.startswith('~'):
                    continue
                if os.path.isfile(full_path):
                    print(f"[Watcher] Detected incoming file: {filename}")
                    if callback:
                        callback(full_path)
            seen_files = current_files
    except KeyboardInterrupt:
        print("\n[Watcher] Stopped monitoring.")
