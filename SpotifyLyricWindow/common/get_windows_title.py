#!/usr/bin/python
# -*- coding:utf-8 -*-
import ctypes

import psutil

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
IsWindowVisible = ctypes.windll.user32.IsWindowVisible


def get_spotify_pid():
    spotify_pid = 0

    def foreach_window(hwnd, lParam):
        nonlocal spotify_pid
        if IsWindowVisible(hwnd):
            buff2 = bytes(4)
            GetWindowThreadProcessId(hwnd, buff2)
            pid = int.from_bytes(buff2, byteorder='little')
            if psutil.Process(pid).name() == "Spotify.exe":
                spotify_pid = pid
                return True
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return spotify_pid


def get_pid_title(pid_):
    spotify_title = ""

    def foreach_window2(hwnd, lParam):
        nonlocal spotify_title
        if IsWindowVisible(hwnd):
            buff2 = bytes(4)
            GetWindowThreadProcessId(hwnd, buff2)
            pid = int.from_bytes(buff2, byteorder='little')
            if pid_ == pid:
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                spotify_title = buff.value
                return True
        return True

    EnumWindows(EnumWindowsProc(foreach_window2), 0)
    return spotify_title



if __name__ == "__main__":
    print(get_spotify_pid())
    print(get_pid_title(15804))
