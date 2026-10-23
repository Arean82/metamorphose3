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

"""
Helper functions available throughout Metamorphose.
"""

import errno
import locale
import os
import time

import app
import wx
import wx.html

try:
    from PIL import Image
except ImportError:
    pass


import hashlib


def compute_file_hash(filepath, algorithm='sha256', chunk_size=65536):
    """Compute cryptographic hash of a file."""
    if not os.path.isfile(filepath):
        return None
    hasher = hashlib.new(algorithm)
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def verify_file_checksum(orig_path, renamed_path, algorithm='sha256'):
    """Verify that original and renamed files have identical contents."""
    h1 = compute_file_hash(orig_path, algorithm)
    h2 = compute_file_hash(renamed_path, algorithm)
    return h1 is not None and h1 == h2


def is_pil_loaded():
    """Determine if the python imaging library is loaded."""
    try:
        Image
    except NameError:
        return False
    else:
        return True


def set_min_size(parent, ignoreCtrls=(), ignoreClasses=()):
    """Recursively set all sizes to platform defaults
    (modified from Boa-Constructor)"""
    # need this for some cases in linux, otherwise cuts off text
    if wx.Platform == '__WXGTK__' and isinstance(parent, wx.StaticText):
        textSize = parent.GetTextExtent(parent.GetLabel())
        size = wx.Size(textSize[0] + 2, -1)
    else:
        size = wx.DefaultSize

    parent.SetMinSize(size)
    parent.SetSize(size)

    for child in parent.GetChildren():
        if child not in ignoreCtrls and not isinstance(child, ignoreClasses):
            set_min_size(child, ignoreCtrls, ignoreClasses)


def adjust_exact_buttons(parent, ignore=()):
    """
    Adjust button sizes when using BU_EXACTFIT

    ignore = tuple of buttons to ignore
    """
    for child in parent.GetChildren():
        if isinstance(child, wx.Button) and child.GetName() not in ignore:
            txt = child.GetLabel()
            size = wx.Size(child.GetTextExtent(txt)[0] + 18, -1)
            child.SetMinSize(size)


def safe_makedir(dir):
    """Create a folder."""
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except OSError as error:
            if error.errno == errno.EEXIST:
                pass
            else:
                make_err_msg(str(error), u"Error")
                pass


def init_environment():
    """Create necessary folders."""
    dirs = ('undo', 'configs')
    for d in dirs:
        safe_makedir(get_user_path(d))


def calc_slice_pos(s, l):
    """Calculate the correct start and end positions for slices."""
    if s == -1 and l == 1:
        frm = -1
        to = None
    elif s < 0 and l > 1:
        frm = s#-l+1
        to = s + l
        if to >= 0:
            to = None
    else:
        frm = s
        to = s + l
    return frm, to


def make_yesno_dlg(msg, title):
    """Show a generic yes / no choice message dialog."""
    dlg = wx.MessageDialog(None, msg, title, wx.YES_NO | wx.YES_DEFAULT | wx.ICON_WARNING)
    if dlg.ShowModal() == wx.ID_YES:
        returnValue = True
    else:
        returnValue = False
    dlg.Destroy()
    return returnValue


def make_err_msg(msg, title=None):
    """Make a generic error message dialog."""
    if not title:
        title = _(u"Error")
    dlg = wx.MessageDialog(None, msg, title, wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


def make_warn_msg(msg, title=None):
    """Make a generic warning message dialog."""
    if not title:
        title = _(u"Warning")
    dlg = wx.MessageDialog(None, msg, title, wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()


def make_info_msg(msg, title=None):
    """Make a generic info message dialog."""
    if not title:
        title = _(u"Information")
    dlg = wx.MessageDialog(None, msg, title, wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def leading_int(text):
    """Return the integer formed by the leading digits, or 0 if there are none."""
    digits = ''
    for char in text:
        if not char.isdigit():
            break
        digits += char
    if not digits:
        return 0
    return int(digits)


def strip_operation_number(text):
    """Remove the leading 'N: ' prefix the operation list adds to a name."""
    head, separator, tail = text.partition(': ')
    if separator and head.isdigit():
        return tail
    return text


def get_user_path(file):
    """Return user's default config path, supporting XDG on Unix."""
    if os.name != 'nt':
        legacy_dir = os.path.join(os.path.expanduser('~'), app.homedir)
        xdg_base = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')
        xdg_dir = os.path.join(xdg_base, 'metamorphose3')
        # Preserve existing legacy directory if user already has configurations there
        if os.path.exists(legacy_dir) and not os.path.exists(xdg_dir):
            return os.path.join(legacy_dir, file)
        return os.path.join(xdg_dir, file)
    base = wx.StandardPaths.Get().GetUserConfigDir()
    return os.path.join(base, app.homedir, file)


def icon_path(icon):
    """Get the full icon path."""
    return app.get_real_path(u'icons/%s' % icon)


def reset_counter(parent, tools, c):
    """Reset a numbering counter."""
    tools.opButtonsPanel.parser.counter = c
    tools.opButtonsPanel.parser.auxCount = 0
    parent.numberingPanel.set_number_params(True)


def write_file(path, data):
    """Write to a file."""
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass
    try:
        fp = open(path, 'w', encoding='utf_8', newline='')
    except (IOError, OSError) as error:
        make_err_msg(str(error), _(u"Error"))
        pass
    else:
        fp.write(str(data))
        fp.close()


def get_notebook_page_names(parent):
    """
    Get all notebook page names.

    parent = notebook object.
    """
    pages = []
    for i in range(parent.notebook.GetPageCount()):
        pages.append(parent.notebook.GetPage(i))
    return pages


def dev_null(event):
    """
    Do nothing.

    Sometimes need to bind this to wx.Event.
    """
    pass


def udate(main, format, itemDateTime):
    """Format a date/time for display."""
    return time.strftime(format, itemDateTime)


def set_busy(busy):
    """Set the application as busy, disable user input."""
    if busy:
        wx.BeginBusyCursor()
    else:
        wx.EndBusyCursor()


def get_encoding_choices(key):
    """Return valid encodings tuple for a given language type."""
    encodingLookup = {
        _(u"Use System Default"): (getattr(locale, 'getencoding', None)() if hasattr(locale, 'getencoding') else locale.getpreferredencoding(False), ),
        _(u'All Languages / Unicode'): (
            u'utf_8', u'utf_16'
        ),
        _(u'Western Europe'): (
            u'windows-1252', u'iso-8859-1', u'iso-8859-15',
            u'mac_roman', u'cp500', u'cp850', u'cp1140'
        ),
        _(u'Central & Eastern Europe'): (
            u'windows-1250', u'iso-8859-2', u'mac_latin2', u'cp852'
        ),
        _(u'Esperanto, Maltese'): (
            u'iso-8859-3'
        ),
        _(u'Nordic Languages'): (
            u'iso-8859-10', u'mac_iceland', u'cp861', u'cp865'
        ),
        _(u'Celtic Languages'): (
            u'iso8859_14',
        ),
        _(u'Baltic Languages'): (
            u'windows-1257', u'iso-8859-13', u'cp775'
        ),
        _(u'Cyrillic Languages'): (
            u'windows-1251', u'iso-8859-5', u'koi8_r', 'koi8_u',
            u'mac_cyrillic', u'cp154', u'cp866', u'cp855'
        ),
        _(u'Greek'): (
            u'windows-1253', u'iso-8859-7', u'mac_greek', u'cp737',
            u'cp869', u'cp875'
        ),
        _(u'Turkish'): (
            u'windows-1254', u'iso-8859-9', u'mac_turkish',
            u'cp857', u'cp1026'
        ),
        _(u'Hebrew'): (
            u'windows-1255', u'iso-8859-8', u'cp424', u'cp856', u'cp862'
        ),
        _(u'Arabic'): (
            u'windows-1256', u'iso-8859-6', u'cp864'
        ),
        _(u'Urdu'): (
            u'cp1006'
        ),
        _(u'Thai'): (
            u'cp874'
        ),
        _(u'Vietnamese'): (
            u'windows-1258'
        ),
        _(u'Traditional Chinese'): (
            u'ms950', u'big5hkscs', u'big5'
        ),
        _(u'Simplified Chinese'): (
            u'gb2312', u'hz'
        ),
        _(u'Unified Chinese'): (
            u'ms936', u'gb18030'
        ),
        _(u'Korean'): (
            u'ms949', u'iso-2022-kr', u'ms1361', u'euc_kr'
        ),
        _(u'Japanese'): (
            u'ms-kanji', u'iso-2022-jp', u'shift_jis', u'euc_jp',
            u'iso-2022-jp-1', u'iso-2022-jp-2004', u'iso-2022-jp-3',
            u'iso-2022-jp-ext', u'shift_jis_2004', u'shift_jisx0213',
            u'euc_jis_2004', u'euc_jisx0213'),
        }
    return encodingLookup[key]


def get_context_menu_path():
    """Return path to user desktop context menu service file."""
    return os.path.expanduser("~/.local/share/kio/servicemenus/metamorphose3.desktop")


def is_context_menu_enabled():
    """Check if file manager context menu integration is active."""
    return os.path.isfile(get_context_menu_path())


def set_context_menu_enabled(enable=True):
    """Enable or disable desktop file manager context menu integration."""
    target_path = get_context_menu_path()
    if enable:
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            content = (
                "[Desktop Entry]\n"
                "Type=Service\n"
                "ServiceTypes=KonqPopupMenu/Plugin,inode/directory\n"
                "Actions=openInMetamorphose\n"
                "X-KDE-Priority=TopLevel\n\n"
                "[Desktop Action openInMetamorphose]\n"
                "Name=Open in Métamorphose 3\n"
                "Icon=metamorphose3\n"
                "Exec=python3 /git/metamorphose3/src/metamorphose3.py -p \"%U\"\n"
            )
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False
    else:
        try:
            if os.path.exists(target_path):
                os.remove(target_path)
            return True
        except Exception:
            return False
