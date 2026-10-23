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

import os

from . import opButtons
import utils
import wx

[wxID_PANEL, wxID_DIRECTORYTEXT, wxID_RADIOBUTTON1,
    wxID_RADIOBUTTON2, wxID_ADDCURRENT, wxID_PATHRECUR,
    wxID_INVERSE, wxID_BROWSE, wxID_ADDBYFILENAME,
    wxID_USEFILEEXT, wxID_USEFILENAME
 ] = [wx.NewIdRef() for __init_ctrls in range(11)]


class Panel(wx.Panel):
    """This is the panel in charge of directory manipulations."""
    def __init_sizer(self):
        pathSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathSizer.Add(self.browse, 0, wx.TOP | wx.LEFT | wx.ALIGN_CENTER, 5)
        pathSizer.Add(self.directoryText, 1, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)

        absSizer = wx.BoxSizer(wx.HORIZONTAL)
        absSizer.Add(self.addCurrent, 0, wx.ALIGN_CENTER)
        absSizer.Add(self.staticText2, 0, wx.ALIGN_CENTER | wx.LEFT, 15)
        absSizer.Add(self.pathRecur, 0, wx.ALIGN_CENTER | wx.LEFT, 5)
        absSizer.Add(self.inverse, 0, wx.ALIGN_CENTER | wx.LEFT, 10)
        
        fileNameSizer = wx.BoxSizer(wx.HORIZONTAL)
        fileNameSizer.Add(self.addByFileName, 0, wx.ALIGN_CENTER)
        fileNameSizer.Add(self.useFileName, 0, wx.ALIGN_CENTER | wx.LEFT, 15)
        fileNameSizer.Add(self.useFileExt, 0, wx.ALIGN_CENTER | wx.LEFT, 5)

        superSizer = wx.BoxSizer(wx.VERTICAL)
        superSizer.Add(self.staticText1, 0, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
        superSizer.Add(pathSizer, 0, wx.EXPAND)
        superSizer.Add(self.staticText3, 1, wx.LEFT, 100)
        superSizer.Add((-1, 25), 0)
        superSizer.Add(self.opButtonsPanel, 0, wx.EXPAND)
        superSizer.Add((-1, 15), 0)
        superSizer.Add(absSizer, 0, wx.ALL, 5)
        superSizer.Add((-1, 10), 0)
        superSizer.Add(fileNameSizer, 0, wx.ALL, 5)

        self.SetSizerAndFit(superSizer)

    def __init_ctrls(self, prnt):
        wx.Panel.__init__(self, id=wxID_PANEL, name=u'directoryToolsPanel',
                          parent=prnt, style=wx.TAB_TRAVERSAL)

        self.opButtonsPanel = opButtons.Panel(self, main)

        self.staticText1 = wx.StaticText(id=-1,
                                         label=_(u"Name (absolute paths allowed):"), name='staticText1',
                                         parent=self, style=0)

        self.browse = wx.Button(id=wxID_BROWSE, label=_(u"Browse"),
                                name=u'browse', parent=self, style=0)
        self.browse.SetToolTip(_(u"Browse for path"))
        self.browse.Bind(wx.EVT_BUTTON, self.browse_for_dir,
                         id=wxID_BROWSE)

        self.directoryText = wx.TextCtrl(id=wxID_DIRECTORYTEXT,
                                         name=u'directoryText', parent=self, value=u'',
                                         style=wx.TE_PROCESS_ENTER)
        self.directoryText.Bind(wx.EVT_TEXT, self.correct_path_type,
                                id=wxID_DIRECTORYTEXT)
        self.directoryText.Bind(wx.EVT_TEXT_ENTER, self.correct_path_enter,
                                id=wxID_DIRECTORYTEXT)

        self.addCurrent = wx.Button(id=wxID_ADDCURRENT,
                                    label=_(u"Copy Path Structure"), name=u'addCurrent', parent=self,
                                    style=0)
        self.addCurrent.SetToolTip(_(u"For best results, use with absolute paths."))
        self.addCurrent.Bind(wx.EVT_BUTTON, self.on_add_current_button,
                             id=wxID_ADDCURRENT)

        self.staticText2 = wx.StaticText(id=-1, label=_(u"Path depth to copy:"),
                                         name='staticText2', parent=self, style=0)

        self.staticText3 = wx.StaticText(id=-1, label=_(u""), name='staticText3',
                                         parent=self, style=0)

        self.pathRecur = wx.SpinCtrl(id=wxID_PATHRECUR, initial=1, max=255,
                                     min=-255, name=u'pathRecur', parent=self, size=wx.Size(65, -1),
                                     style=wx.SP_ARROW_KEYS | wx.TE_PROCESS_ENTER, value='1')
        self.pathRecur.SetValue(1)
        self.pathRecur.SetToolTip(_(u"Negative values allowed"))
        self.pathRecur.Bind(wx.EVT_TEXT_ENTER, main.show_preview,
                            id=wxID_PATHRECUR)
        self.pathRecur.Bind(wx.EVT_SPINCTRL, main.show_preview,
                            id=wxID_PATHRECUR)

        self.inverse = wx.CheckBox(id=wxID_INVERSE, label=_(u"inverse"),
                                   name=u'inverse', parent=self, style=0)
        self.inverse.SetToolTip(_(u"Start from begining or end of path"))
        self.inverse.SetValue(False)
        self.inverse.Bind(wx.EVT_CHECKBOX, main.show_preview)

        self.addByFileName = wx.Button(id=wxID_ADDBYFILENAME,
                                       label=_(u"Copy File Name"), name=u'addByFileName', parent=self,
                                       style=0)
        self.addByFileName.SetToolTip(_(u"Add a directory with the same name as the file."))
        self.addByFileName.Bind(wx.EVT_BUTTON, self.on_add_by_filename_button,
                                id=wxID_ADDBYFILENAME)

        self.useFileName = wx.CheckBox(id=wxID_USEFILENAME, label=_(u"Name"),
                                       name=u'inverse', parent=self, style=0)
        self.useFileName.SetToolTip(_(u"Add the file name"))
        self.useFileName.SetValue(True)
        self.useFileName.Bind(wx.EVT_CHECKBOX, main.show_preview)

        self.useFileExt = wx.CheckBox(id=wxID_USEFILEEXT, label=_(u"Extension"),
                                      name=u'useFileExt', parent=self, style=0)
        self.useFileExt.SetToolTip(_(u"Add the file extension"))
        self.useFileExt.SetValue(False)
        self.useFileExt.Bind(wx.EVT_CHECKBOX, main.show_preview)

    def __init__(self, parent, main_window):
        global main
        main = main_window
        self.__init_ctrls(parent)
        self.__init_sizer()
        self.staticText3.Show(False)
        self.activatedField = self.directoryText
        # text is accessed by parent
        self.params = {
            'pathStructTxt': ':' + _(u"Path-Structure") + ':',
            'nameTxt': ':' + _(u"File-Name") + ':'
            }

    def on_add_by_filename_button(self, event):
        """Add file name."""
        self.__to_directory_text(self.params['nameTxt'])

    def on_add_current_button(self, event):
        """Add current directory."""
        self.__to_directory_text(self.params['pathStructTxt'])

    def __to_directory_text(self, text):
        iPoint = self.directoryText.GetInsertionPoint()
        self.directoryText.WriteText(text)
        self.directoryText.SetFocus()
        self.directoryText.SetInsertionPoint(iPoint + len(text))

    def browse_for_dir(self, event):
        """Browse for directoryrowse for directory."""
        dlg = wx.DirDialog(self, _(u"Choose a directory:"),
                           style=wx.DD_DEFAULT_STYLE)
        dlg.SetPath(self.directoryText.GetValue())
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.directoryText.SetValue('')
                dir = dlg.GetPath()
                self.__to_directory_text(dir)
        finally: dlg.Destroy()


    # --- CORRECT SOME COMMON MISTAKES --- #
    # preliminary, needs more work!

    #from http://regexlib.com
    r"""
    ^[^\\\./:\*\?\"<>\|]{1}[^\\/:\*\?\"<>\|]{0,254}$
    Validates a long filename using Windows' rules. Requires one
    valid filename character other than "." for the first
    character and then any number of valid filename characters up to a
    total length of 255 characters. Unresolved is how to prevent the
    last character from being a "." while still meeting all
    the features that this regex does now.
    -- Dale Preston
    """

    """
    ([a-zA-Z]:(\\w+)*\\[a-zA-Z0_9]+)?.xls
    This RegEx will help to validate a physical file path with a
    specific file extension (here xls)
    -- vinod kumar
    """

    r"""
    ^(([a-zA-Z]:|\\)\\)?(((\.)|(\.\.)|([^\\/:\*\?"\|<>\. ](([^\\/:\*\?"\|<>\. ])|([^\\/:\*\?"\|<>]*[^\\/:\*\?"\|<>\. ]))?))\\)*[^\\/:\*\?"\|<>\. ](([^\\/:\*\?"\|<>\. ])|([^\\/:\*\?"\|<>]*[^\\/:\*\?"\|<>\. ]))?$
    File Name Validator. Validates both UNC (\\server\share\file) and regular MS path (c:\file).
    -- Dmitry Borysov
    """

    def separator_chars(self):
        """Return the separator to keep and the one to replace."""
        if os.sep == "/":
            return "/", "\\"
        return "\\", "/"

    def normalise_separators(self, path):
        """Replace foreign separators and collapse duplicated ones, preserving UNC prefixes."""
        keep, replace = self.separator_chars()
        text = "".join(keep if char == replace else char for char in path)
        is_unc = (keep == "\\") and text.startswith("\\\\") and not text.startswith("\\\\\\")
        prefix = "\\\\" if is_unc else ""
        remainder = text[2:] if is_unc else text
        doubled = keep + keep
        while doubled in remainder:
            remainder = remainder.replace(doubled, keep)
        return prefix + remainder

    def has_bad_separators(self, path):
        """True when the path uses a foreign separator or repeats one (preserving UNC prefix)."""
        keep, replace = self.separator_chars()
        if replace in path:
            return True
        is_unc = (keep == "\\") and path.startswith("\\\\") and not path.startswith("\\\\\\")
        remainder = path[2:] if is_unc else path
        return (keep + keep) in remainder

    # user presses enter, errors fixed
    def correct_path_enter(self, event):
        path = self.directoryText.GetValue()
        # fix
        newpath = self.normalise_separators(path)
        self.directoryText.SetValue(newpath)
        self.directoryText.SetInsertionPointEnd()
        self.staticText3.Show(False)
        # apply
        self.directoryText.SetBackgroundColour(u'#FFFFFF')
        self.directoryText.Refresh()
        self.enable_notebook_tabs(event)

    # user types, warning shown
    def correct_path_type(self, event):
        path = self.directoryText.GetValue()
        # warn
        if self.has_bad_separators(path):
            err = _(u"Incorrect path separator")
            self.staticText3.SetLabel(_(u"%s - press ENTER to fix") % err)
            utils.set_min_size(self.staticText3, 0)
            self.directoryText.SetBackgroundColour(u"#FDEB22")
            self.directoryText.Refresh()
            self.staticText3.Show(True)
        # apply
        else:
            main.show_preview(event)



    # is the path structure an absolute path?
    """
    def checkAbs(self, event):
        path = self.directoryText.GetValue()
        absPathWidgets = (self.addCurrent, self.staticText2, self.pathRecur, self.inverse)
        if os.path.isabs(path):
            for widget in absPathWidgets:
                widget.Enable(True)
        else:
            for widget in absPathWidgets:
                widget.Enable(False)
        main.show_preview(event)
    """
