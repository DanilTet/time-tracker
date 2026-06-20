import ctypes

DESKTOP_SWITCHDESKTOP = 0x0100


def is_screen_locked():
    # true если єкран заблочен
    user32 = ctypes.windll.user32
    desktop = user32.OpenInputDesktop(0, False, DESKTOP_SWITCHDESKTOP)

    if desktop == 0:
        return True  # если не смогли открыть значит заблокирован

    user32.CloseDesktop(desktop)
    return False