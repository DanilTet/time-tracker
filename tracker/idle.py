import ctypes


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


def get_idle_seconds():
    # возращает колво секунд с последнего ввода
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))

    millis_since_last_input = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis_since_last_input / 1000.0