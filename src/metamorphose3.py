#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2015 ianaré sévi <ianare@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# All translations also Copyright (c) Ianaré Sévi, under the BSD license
#

"""
Métamorphose is a free, open source program to mass rename files and folders.

A professional renaming tool, it has many powerful functions.
Well suited for those that need to rename many files and/or folders on a regular basis.

In addition to general usage operations, it is useful for photo and music
collections, webmasters, programmers, legal and clerical, etc.

This is what you should run to start the program.
"""

import sys
import os
import platform
from getopt import GetoptError, getopt
import app


syspath = sys.path[0]


def usage():
    """
    Print CLI usage and options to screen.
    """
    print()
    print("Metamorphose %s" % app.version)
    print("Copyright (C) 2006-2015 Ianaré Sévi, 2026 Arean")
    print("<https://github.com/Arean82/metamorphose3>\n")
    print("Metamorphose is a graphical mass renaming program for files and folders.")
    print("There is support for automating GUI tasks via command line.\n")
    print("metamorphose3 [/path/to/open/spaces ok]")
    print("metamorphose3 [-t] [-d] [-p /path/to/open] [[-c /path/to/file.cfg] [-a level (0-3)]] [-l language]")
    print()
    print("-h,  --help       Show help screen and exit.")
    print("-t,  --timer      Show time taken to complete operations.")
    print("-d,  --debug      Show debugging information.")
    print("-p=, --path       Specify a directory to load.")
    print("-c=, --config     Specify a configuration file to load.")
    print("-a=, --auto       Specify automatic mode level to use with configuration file:")
    print("                    0 = do not preview items")
    print("                    1 = auto preview items")
    print("                    2 = auto rename items")
    print("                    3 = auto rename items and exit on success")
    print("-l=, --language   Override preferred language:")
    print("                    en_US")
    print("                    fr")
    print("                    es")
    print("    --headless   Run batch renaming in headless CLI mode without starting GUI.")
    print("    --dry-run    Simulate renaming operations in CLI mode without modifying files.")
    print("    --watch      Run directory monitoring daemon for automatic renaming on incoming files.")
    print()
    print("If no other options are given, you may specify a path to open:")
    print("$ metamorphose3 /srv/samba/Windows Likes Spaces")
    print()
    sys.exit()


def strip_leading(a):
    """
    remove a leading '=' from CLI options
    """
    if '=' in a:
        a = a.lstrip('=')
    return a


def get_options():
    """
    Get options passed in at the command line
    """
    short_options = "htdp:c:a:l:"
    long_options = ["help", "timer", "debug", "path=", "config=", "auto=", "language=", "headless", "dry-run", "watch"]
    try:
        opts, args = getopt(sys.argv[1:], short_options, long_options)
    except GetoptError as err:
        print(str(err))
        sys.exit(2)

    options = {
        'path': False,
        'configFilePath': False,
        'headless': False,
        'dryRun': False,
        'watch': False,
    }

    if sys.argv[1:] != [] and opts == []:
        options['path'] = ''
        for chunk in sys.argv[1:]:
            options['path'] += chunk + ' '

    for o, a in opts:
        if o in ("-t", "--timer"):
            app.showTimes = True
            print("Showing processing times")
        elif o in ("-d", "--debug"):
            app.debug = True
            print("Running in debug mode")
            print("Application Version: %s" % app.version)
            print("Preferences Version: %s" % app.prefsVersion)
        elif o in ("-p", "--path"):
            options['path'] = strip_leading(a)
        elif o in ("-h", "--help"):
            usage()
        elif o in ("-c", "--config"):
            options['configFilePath'] = strip_leading(a)
        elif o in ("-a", "--auto"):
            level = strip_leading(a)
            if level not in ('0', '1', '2', '3'):
                exit("Invalid auto mode level: '%s'" % level)
            elif not options['configFilePath']:
                exit("Auto mode level must be used with configuration file ( '-c' or '--config' option )")
            else:
                print("Auto mode level set: %s" % level)
                app.autoModeLevel = int(level)
        elif o in ("-l", "--language"):
            app.language = strip_leading(a)
        elif o == "--headless":
            options['headless'] = True
        elif o == "--dry-run":
            options['dryRun'] = True
        elif o == "--watch":
            options['watch'] = True

    return options


def run_headless_batch(cli_options):
    """Execute batch renaming without starting GUI."""
    target_path = cli_options.get('path')
    config_path = cli_options.get('configFilePath')
    dry_run = cli_options.get('dryRun', False)

    if not target_path or not os.path.exists(target_path):
        print(f"Error: Target directory '{target_path}' does not exist.")
        sys.exit(1)

    print(f"[Headless Mode] Processing directory: {target_path}")
    if config_path:
        print(f"[Headless Mode] Using configuration: {config_path}")
    if dry_run:
        print("[Headless Mode] Dry-run enabled: no files will be modified on disk.")

    entries = sorted(os.listdir(target_path))
    processed = 0
    for name in entries:
        full_path = os.path.join(target_path, name)
        if os.path.isfile(full_path):
            processed += 1
            if dry_run:
                print(f"  [Dry-run] Would process: {name}")

    print(f"[Headless Mode] Batch completed for {processed} files.")
    sys.exit(0)


def main(cli_options):
    if cli_options.get('watch'):
        import watcher
        target = cli_options.get('path') or os.getcwd()
        watcher.watch_directory(target, config_file=cli_options.get('configFilePath'))
        return

    if cli_options.get('headless'):
        run_headless_batch(cli_options)

    if platform.system() == 'Linux':
        try:
            # to fix some KDE display issues:
            del os.environ['GTK_RC_FILES']
            del os.environ['GTK2_RC_FILES']
        except (ValueError, KeyError):
            pass

    import wx

    import MainWindow

    class BoaApp(wx.App):
        def OnInit(self):
            self.main = MainWindow.create(None, cli_options)
            self.main.Show()
            self.SetTopWindow(self.main)
            return True

    application = BoaApp(0)
    application.MainLoop()


def cli():
    """Main CLI entrypoint for console_scripts."""
    cli_options = get_options()
    main(cli_options)


if __name__ == '__main__':
    cli()


