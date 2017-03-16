from collections import namedtuple

import ctypes
from ctypes import wintypes


def check_zero(result, func, args):
    if not result:
        err = ctypes.get_last_error()
        if err:
            raise ctypes.WinError(err)
    return args


psapi = ctypes.WinDLL('psapi', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

WindowInfo = namedtuple('WindowInfo', 'title pid handle')

WNDENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND, # _In_ hWnd
    wintypes.LPARAM, ) # _In_ lParam

user32.EnumWindows.errcheck = check_zero
user32.EnumWindows.argtypes = (
    WNDENUMPROC, # _In_ lpEnumFunc
    wintypes.LPARAM,) # _In_ lParam

user32.GetForegroundWindow.errcheck = check_zero

user32.SetForegroundWindow.errcheck = check_zero
user32.SetForegroundWindow.argtypes = (
    wintypes.HWND,) # _In_ hWnd

user32.IsWindowVisible.argtypes = (
    wintypes.HWND,) # _In_ hWnd

user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = (
    wintypes.HWND, # _In_      hWnd
    wintypes.LPDWORD,) # _Out_opt_ lpdwProcessId

user32.GetWindowTextLengthW.errcheck = check_zero
user32.GetWindowTextLengthW.argtypes = (
    wintypes.HWND,) # _In_ hWnd

user32.GetWindowTextW.errcheck = check_zero
user32.GetWindowTextW.argtypes = (
    wintypes.HWND, # _In_  hWnd
    wintypes.LPWSTR, # _Out_ lpString
    ctypes.c_int,)   # _In_  nMaxCount

psapi.EnumProcesses.errcheck = check_zero
psapi.EnumProcesses.argtypes = (
    wintypes.LPDWORD, # _Out_ pProcessIds
    wintypes.DWORD, # _In_  cb
    wintypes.LPDWORD,) # _Out_ pBytesReturned


def list_windows():
    """ Return a sorted list of visible windows.

    :return:
    """
    result = []

    @WNDENUMPROC
    def enum_proc(hWnd, lParam):
        if user32.IsWindowVisible(hWnd):
            pid = wintypes.DWORD()
            tid = user32.GetWindowThreadProcessId(
                hWnd, ctypes.byref(pid))
            length = user32.GetWindowTextLengthW(hWnd) + 1
            title = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hWnd, title, length)
            result.append(WindowInfo(title.value, pid.value, hWnd))
        return True

    user32.EnumWindows(enum_proc, 0)
    return sorted(result)
