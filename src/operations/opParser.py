# -*- coding: utf-8 -*-

# Copyright (C) 2006-2013 ianaré sévi <ianare@gmail.com>
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
# Contributions:
#
# 2007-01-17
#  __to_alpha function by Gustavo Niemeyer (gustavo@niemeyer.net)

import calendar
import gettext
import locale
import os
import sys
import time

try:
    _
except NameError:
    _ = gettext.gettext

import exifread as EXIF
import app
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
from . import roman
import utils
import video_meta

IMAGE_EXTENSIONS = ('tif', 'tiff', 'jpg', 'jpeg', 'jtif', 'thm')
AUDIO_EXTENSIONS = ('ape', 'asf', 'flac', 'm4a', 'mp3', 'ogg')
VIDEO_EXTENSIONS = ('mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v', 'mpg', 'mpeg', 'ts')
PDF_EXTENSIONS = ('pdf',)

PDF_INFO = {
    _('pdf title'): 'title',
    _('pdf author'): 'author',
    _('pdf subject'): 'subject',
}

def read_pdf_metadata(filepath):
    """Pure-python lightweight PDF trailer / Info dict parser."""
    meta = {}
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            info_idx = content.rfind(b'/Info')
            if info_idx != -1:
                chunk = content[info_idx:info_idx + 1024].decode('latin-1', 'ignore')
                import re
                t_match = re.search(r'/Title\s*\(([^)]+)\)', chunk)
                if t_match:
                    meta['title'] = t_match.group(1)
                a_match = re.search(r'/Author\s*\(([^)]+)\)', chunk)
                if a_match:
                    meta['author'] = a_match.group(1)
                s_match = re.search(r'/Subject\s*\(([^)]+)\)', chunk)
                if s_match:
                    meta['subject'] = s_match.group(1)
    except Exception:
        pass
    return meta

VIDEO_INFO = {
    _('duration'): 'duration',
    _('video width'): 'width',
    _('video height'): 'height',
    _('video codec'): 'videocodec',
    _('audio codec'): 'audiocodec',
    _('frame rate'): 'framerate',
}


def split_non_digits(text):
    """Split text into runs of digits, dropping everything else."""
    parts = []
    current = ''
    for char in text:
        if char.isdigit():
            current += char
        elif current:
            parts.append(current)
            current = ''
    if current:
        parts.append(current)
    return parts

def write_audio_tag(filepath, tag_name, value):
    """Write updated metadata tag directly back into audio file header."""
    if not os.path.isfile(filepath):
        return False
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.mp3':
            from mutagen.easyid3 import EasyID3
            audio = EasyID3(filepath)
            audio[tag_name] = [str(value)]
            audio.save()
            return True
        elif ext in ('.flac', '.ogg'):
            from mutagen import File
            audio = File(filepath)
            if audio is not None:
                audio[tag_name] = [str(value)]
                audio.save()
                return True
        elif ext in ('.m4a', '.mp4'):
            from mutagen.easymp4 import EasyMP4
            audio = EasyMP4(filepath)
            audio[tag_name] = [str(value)]
            audio.save()
            return True
    except Exception:
        pass
    return False
    """Split text into runs of digits, dropping everything else."""
    parts = []
    current = ''
    for char in text:
        if char.isdigit():
            current += char
        elif current:
            parts.append(current)
            current = ''
    if current:
        parts.append(current)
    return parts


# Metadata tag translations

AUDIO_INFO = {
    _('title'): "title",
    _('version'): "version",
    _('album'): "album",
    _('track number'): "tracknumber",
    _('artist'): "artist",
    _('genre'): "genre",
    _('performer'): "performer",
    _('date'): "date",
    _('author'): "author",
    _('composer'): "composer",
    _('conductor'): "conductor",
    _('lyricist'): "lyricist",
    _('disc number'): "discnumber",
    _('language'): "language",
    _('encoded by'): "encodedby",
    _('comment'): 'comment',
    _('bitrate'): 'bitrate',
    _('sample rate'): 'samplerate',
}

IMAGE_INFO = {
    _(u"width"): u"EXIF ExifImageWidth",
    #_(u"date taken") : u'EXIF DateTimeOriginal',
    #_(u"date modified") : u'Image DateTime',
    _(u"height"): u"EXIF ExifImageLength",
    _(u"exposure"): u"EXIF ExposureTime",
    _(u"F-stop"): u"EXIF FNumber",
    _(u"flash"): u"EXIF Flash",
    _(u"focal-length"): u"EXIF FocalLength",
    _(u"ISO"): u"EXIF ISOSpeedRatings",
    _(u"shutter-speed"): u"EXIF ShutterSpeedValue",
    _(u"aperture"): u"EXIF ApertureValue",
    _(u"copyright"): u"Image Copyright",
    _(u"make"): u"Image Make",
    _(u"model"): u"Image Model",
    _(u"orientation"): u"Image Orientation",
    _(u"unit"): u"Image ResolutionUnit",
    _(u"X-resolution"): u"Image XResolution",
    _(u"Y-resolution"): u"Image YResolution",
    _(u"X-res"): u"Image XResolution",
    _(u"Y-res"): u"Image YResolution",
    _(u"software"): u"Image Software"
}


class Parser():
    def __init__(self, main_window):
        app.debug_print("loading operations parser");
        global main
        main = main_window
        self.reset()

    def reset(self):
        self.counter = 0
        self.auxCount = 0

    def __add_to_warnings(self, path, msg):
        """Add an item to warnings."""
        ec = main.ec
        if main.warn.count(ec) < 1:
            main.warn.append(ec)
            main.errorLog.insert(0, (ec, path, msg, u'warn'))

    def __add_to_errors(self, path, msg):
        """Add an item to errors."""
        ec = main.ec
        if main.bad.count(ec) < 1:
            main.bad.append(ec)
            main.errorLog.insert(0, (ec, path, msg, u'bad'))

#--- FOLDER ------------------------------------------------------------------#
    def __add_folder(self, file, depth):
        splitPath = file.split(os.sep)
        try:
            folder = splitPath[-(int(depth) + 1)]
        except (ValueError, IndexError):
            return ''
        else:
            return folder

#--- NUMBERING ---------------------------------------------------------------#
    def __to_alpha(self, i):
        s = ''
        while i:
            i -= 1
            q, m = divmod(i, 26)
            s = chr(97 + m) + s
            i = q
        return s

    def __enumber(self, file, operation):
        numberStyle = operation.numberingPanel.Style
        numberParams = operation.numberingPanel.Params
        start = numberParams[0]
        count = numberParams[1]
        reset = numberParams[2]
        dirReset = numberParams[3]
        countByDir = numberParams[4]
        repeat = numberParams[5]
        maxNumb = numberParams[6]
        incrementOnDiff = numberParams[7]

        lastDir = main.lastDir
        curDir = main.curDir
        lastName = main.lastName
        curName = main.curName

        maxNumb = abs((len(main.items) + (start-1)) * count)
        if repeat > 0:
            maxNumb = maxNumb / (repeat + 1)

        # to reset count by directory
        if lastDir != curDir and lastDir is not False and dirReset:
            self.counter = 0
        if lastDir != curDir and lastDir is not False and countByDir:
            self.counter += 1

        # to reset by identical name
        if incrementOnDiff and curName is not False and lastName != curName:
            self.counter = 0

        # calculate current number based on user settings:
        i = start + (self.counter * int(count))

        # numerical counting:
        if numberStyle[0] == u'digit':
            padChar = str(numberStyle[1])
            # padding enabled and non-empty pad charcter:
            if numberStyle[3] and padChar:
                if numberStyle[2] == u'auto':
                    padWidth = len(str(maxNumb))
                    y = str(i).rjust(padWidth, padChar)
                else:
                    y = str(i).rjust(int(numberStyle[2]), padChar)
            # no padding:
            else:
                y = i

        # alphabetical numbering:
        elif numberStyle[0] == u'alpha':
            i = abs(i)

            if i == 0:
                i = 1
            y = self.__to_alpha(i)
            # uppercase
            if numberStyle[1]:
                y = y.upper()

        # roman numerals
        elif numberStyle[0] == u'roman':
            try:
                y = roman.toRoman(i)
                if not numberStyle[1]:
                    y = y.lower()
            except Exception:
                if main.bad.count(main.ec) < 1:
                    main.bad.append(main.ec)
                    main.errorLog.insert(0, (main.ec, file,
                        _(u"Roman numeral error: %s") % sys.exc_info()[1],
                        u'bad'))
                y = ""

        def increment_reset_count():
            # see if count is at reset level:
            if  self.counter == reset and self.counter != 0:
                self.counter = 0
            elif not countByDir:
                self.counter += 1

        # repeat the same number
        if repeat > 0:
            if self.auxCount == repeat:
                increment_reset_count()
                self.auxCount = 0
            elif self.auxCount < repeat:
                self.auxCount += 1
            else:
                self.auxCount = 0
        else:
            increment_reset_count()
        return str(y)

#--- DATE AND TIME -----------------------------------------------------------#
    def __get_exif_date(self, path, tag):
        ext = os.path.splitext(path)[1][1:].lower()
        if ext.startswith(IMAGE_EXTENSIONS):
            try:
                file = open(path, 'rb')
            except IOError:
                self.__add_to_errors(path, _(u"Could not open file!"))
            else:
                tags = EXIF.process_file(file, details=False, stop_tag=tag)
                # see if the tag exists
                if tag in tags:
                    try:
                        itemDateTime = str(tags[tag])
                        itemDateTime = split_non_digits(itemDateTime)
                        itemDateTime = list(map(int, itemDateTime))
                    except ValueError as err:
                        self.__add_to_warnings(path, _(u"Exif error: %s") % err)
                        return False

                    # attempt to convert tag's text to a date
                    try:
                        dayWeek = calendar.weekday(itemDateTime[0],
                                                   itemDateTime[1],
                                                   itemDateTime[2])
                    # invalid date
                    except ValueError as err:
                        self.__add_to_warnings(path, _(u"Exif error: %s") % err)
                    else:
                        itemDateTime.extend([dayWeek, 1, 0])
                        return itemDateTime
                # date tag doesn't exist
                else:
                    self.__add_to_warnings(path, _(u"Could not read Exif tag"))
                    return False

    def __date_time(self, op, path, operation):
        dateTimePanel = operation.dateTimePanel
        dateTime = dateTimePanel.dateTime
        dateTime[1] = dateTimePanel.dateTestDisplay.GetLabel()
        dateTime[2] = dateTimePanel.timeTestDisplay.GetLabel()

        # user specified date/time
        if not dateTime[0]:
            return dateTime[op + 1]

        # get date/time from item
        else:
            itemTimeType = dateTimePanel.itemTimeType.GetSelection()
            if itemTimeType == 0:
                try: itemDateTime = time.localtime(os.path.getctime(path))
                except WindowsError: return ''
            elif itemTimeType == 1:
                try: itemDateTime = time.localtime(os.path.getmtime(path))
                except WindowsError: return ''
            elif itemTimeType == 2:
                try: itemDateTime = time.localtime(os.path.getatime(path))
                except WindowsError: return ''
            elif itemTimeType == 3:
                itemDateTime = self.__get_exif_date(path, 'EXIF DateTimeOriginal')
            elif itemTimeType == 4:
                itemDateTime = self.__get_exif_date(path, 'Image DateTime')

            if itemDateTime:
                return utils.udate(main, dateTime[op + 1], itemDateTime)
            else:
                return ''

#--- IMAGE METADATA ----------------------------------------------------------#
    def __get_image_tag(self, path, EXIFtags, command):
        tag = IMAGE_INFO[command]

        if tag in EXIFtags:
            return str(EXIFtags[tag])
        else:
            self.__add_to_warnings(path, _(u"Could not read Exif tag"))

#--- AUDIO METADATA ----------------------------------------------------------#
    # (based on 'File' function from mutagen/__init__.py)
    def __get_audio_metadata(self, filename, options=None):
        """Guess the type of the file and try to open it.

        The file type is decided by several things, such as the first 128
        bytes (which usually contains a file type identifier), the
        filename extension, and the presence of existing tags.

        If no appropriate type could be found, None is returned.
        """

        if options is None:
            options = [MP3, TrueAudio, OggTheora, OggSpeex, OggVorbis, OggFLAC,
                FLAC, APEv2File, EasyMP4, ID3FileType, WavPack, Musepack,
                MonkeysAudio, OptimFROG, ASF]

        if not options:
            return None

        try:
            fileobj = open(filename, "rb")
        except IOError:
            self.__add_to_errors(filename, _(u"Could not open file!"))
            return None

        try:
            header = fileobj.read(128)
            # Sort by name after score. Otherwise import order affects
            # Kind sort order, which affects treatment of things with
            # equals scores.
            results = [(Kind.score(filename, fileobj, header), Kind.__name__)
                for Kind in options]
        finally:
            fileobj.close()
        results = list(zip(results, options))
        results.sort(key=lambda item: item[0])
        (score, name), Kind = results[-1]
        if score > 0:
            if Kind.__name__ == 'MP3':
                Kind = EasyID3
            try:
                audioMetadata = Kind(filename)
            except Exception:
                self.__add_to_errors(filename, _(u"Could not read audio metadata"))
                return None
            app.debug_print(audioMetadata)
            return audioMetadata
        else:
            self.__add_to_warnings(filename, _(u"Could not determine audio file type"))
            return None

    def __get_audio_tag(self, audioMetadata, command):
        tag = AUDIO_INFO[command]
        path = audioMetadata.filename
        if tag == "bitrate":
            info = getattr(audioMetadata, 'info', None)
            if info and getattr(info, 'bitrate', None):
                return str(int(info.bitrate // 1000)) + "k"
            return False
        if tag == "samplerate":
            info = getattr(audioMetadata, 'info', None)
            if info and getattr(info, 'sample_rate', None):
                return str(info.sample_rate)
            return False
        if tag in audioMetadata:
            value = audioMetadata[tag][0]
            encoding = app.prefs.get('encodingSelect')
            system_encoding = getattr(locale, 'getencoding', None)() if hasattr(locale, 'getencoding') else locale.getpreferredencoding(False)
            if str(encoding) != str(system_encoding):
                try:
                    # incorrect encodings should default to latin-1
                    # allow forcing an encoding type from preferences
                    value = value.encode('latin-1').decode(encoding)
                except Exception:
                    self.__add_to_warnings(path, _(u"Invalid encoding specified: %s") % encoding)
            if tag == "tracknumber" and len(value) == 1:
                value = "0" + value
            return value
        else:
            self.__add_to_warnings(path, _(u"Could not read tag: %s") % command)
            return False

#--- PARSE INPUT AND FORMAT --------------------------------------------------#
    def parse_input(self, text, file, operation):
        """
        Parse the active fields for sub operations and return
        the corresponding result in place.
        """
        ext = os.path.splitext(file)[1][1:]
        # possible special operations:
        commands = [_(u"numb"), _(u"date"), _(u"time"), _(u"folder")]

        # audio
        audioInfoStart = len(commands)
        for i in AUDIO_INFO.keys():
            commands.append(i)
        audioInfoEnd = len(commands)

        # Exif
        for i in IMAGE_INFO.keys():
            commands.append(i)
        imageInfoEnd = len(commands)

        # Video
        for i in VIDEO_INFO.keys():
            commands.append(i)
        videoInfoEnd = len(commands)

        # PDF
        for i in PDF_INFO.keys():
            commands.append(i)

        parsedText = u''

        # any text in between this character will be considered an operation:
        text = text.strip(u':').split(u':')

        isImage = ext.lower().startswith(IMAGE_EXTENSIONS)
        isAudio = ext.lower().startswith(AUDIO_EXTENSIONS)
        isVideo = ext.lower().startswith(VIDEO_EXTENSIONS)
        isPdf = ext.lower().startswith(PDF_EXTENSIONS)
        audioMetadata = False
        videoMetadata = False
        pdfMetadata = False

        # process here to load Exif metadata only once
        if isImage:
            for segment in text:
                if segment in commands[audioInfoEnd:imageInfoEnd]:
                    try:
                        with open(file, 'rb') as file_rb:
                            imageMetadata = EXIF.process_file(file_rb, details=False)
                    except OSError:
                        imageMetadata = {}
                    break
        # process here to load audio metadata only once
        elif isAudio:
            for segment in text:
                if segment in commands[audioInfoStart:audioInfoEnd]:
                    audioMetadata = self.__get_audio_metadata(file)
                    break
        # process here to load video metadata only once
        elif isVideo:
            for segment in text:
                if segment in commands[imageInfoEnd:videoInfoEnd]:
                    videoMetadata = video_meta.read_video_metadata(file)
                    break
        # process here to load pdf metadata only once
        elif isPdf:
            for segment in text:
                if segment in commands[videoInfoEnd:]:
                    pdfMetadata = read_pdf_metadata(file)
                    break
        # execute functions based on user input:
        for segment in text:
            value = False
            # numbering
            if segment == commands[0]:
                value = self.__enumber(file, operation)
            # date
            elif segment == commands[1]:
                value = self.__date_time(0, file, operation)
            # time
            elif segment == commands[2]:
                value = self.__date_time(1, file, operation)
            # folder name
            elif segment[:len(commands[3])] == commands[3]:
                value = self.__add_folder(file, segment[len(commands[3]):])
            # audio
            elif isAudio and audioMetadata and segment in commands[audioInfoStart:audioInfoEnd]:
                value = self.__get_audio_tag(audioMetadata, segment)
            # EXIF
            elif isImage and segment in commands[audioInfoEnd:imageInfoEnd]:
                value = self.__get_image_tag(file, imageMetadata, segment)
            # Video
            elif isVideo and videoMetadata and segment in commands[imageInfoEnd:videoInfoEnd]:
                tag_key = VIDEO_INFO.get(segment)
                value = videoMetadata.get(tag_key, '')
            # PDF
            elif isPdf and pdfMetadata and segment in commands[videoInfoEnd:]:
                tag_key = PDF_INFO.get(segment)
                value = pdfMetadata.get(tag_key, '')
            # if segment doesn't match a command, reprint segment:
            else:
                parsedText += segment
            if value:
                parsedText += value
        return parsedText
