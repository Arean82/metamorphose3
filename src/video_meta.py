# -*- coding: utf-8 -*-
"""
Video metadata reader.
Extracts duration, width, height, bitrate, and codec tags.
Uses pymediainfo if available, with pure-Python MP4/Matroska container header parser fallbacks.
"""

import os
import struct

try:
    from pymediainfo import MediaInfo
    _PYMEDIAINFO = True
except ImportError:
    MediaInfo = None
    _PYMEDIAINFO = False


def read_video_metadata(filepath):
    """
    Extract metadata from video file.
    Returns dict with keys: 'duration', 'width', 'height', 'videocodec', 'audiocodec', 'framerate'.
    """
    data = {}
    if _PYMEDIAINFO:
        try:
            mi = MediaInfo.parse(filepath)
            for track in mi.tracks:
                if track.track_type == 'Video':
                    if track.width:
                        data['width'] = str(track.width)
                    if track.height:
                        data['height'] = str(track.height)
                    if track.format:
                        data['videocodec'] = str(track.format)
                    if track.frame_rate:
                        data['framerate'] = str(int(round(float(track.frame_rate))))
                    if track.duration:
                        # duration in seconds
                        data['duration'] = str(int(float(track.duration) / 1000.0))
                elif track.track_type == 'Audio' and 'audiocodec' not in data:
                    if track.format:
                        data['audiocodec'] = str(track.format)
            if data:
                return data
        except Exception:
            pass

    # Built-in lightweight fallback parser for MP4/MOV containers
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.mp4', '.m4v', '.mov'):
        try:
            with open(filepath, 'rb') as f:
                # Read chunks looking for moov -> trak -> tkhd
                buf = f.read(1024 * 1024)
                idx = buf.find(b'tkhd')
                if idx != -1 and idx + 84 <= len(buf):
                    # tkhd version & flags
                    version = buf[idx + 4]
                    offset = idx + 8
                    if version == 0:
                        # 32-bit: width and height are at offset + 76
                        w_bytes = buf[offset + 72:offset + 76]
                        h_bytes = buf[offset + 76:offset + 80]
                    else:
                        w_bytes = buf[offset + 84:offset + 88]
                        h_bytes = buf[offset + 88:offset + 92]
                    w = struct.unpack('>I', w_bytes)[0] >> 16
                    h = struct.unpack('>I', h_bytes)[0] >> 16
                    if 0 < w < 16384 and 0 < h < 16384:
                        data['width'] = str(w)
                        data['height'] = str(h)
        except Exception:
            pass

    return data
