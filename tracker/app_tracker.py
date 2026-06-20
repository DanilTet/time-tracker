import time
import win32gui
import win32process
import psutil

def getActiveWindowProcessName():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name()
    except Exception:
        return "Unknown"
    
def main():
    print("Трекер запущен. Ctrl+C чтобі остановить и увидеть итоги.")

    time_per_app = {}
    check_interval = 1 # в секундах

    try:
        while True:
            app_name = getActiveWindowProcessName()
            time_per_app[app_name] = time_per_app.get(app_name, 0) + check_interval
            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\n--- Итоги сессии ---")
        for app, seconds in sorted(time_per_app.items(), key=lambda x: -x[1]):
            minutes = seconds // 60
            sec = seconds % 60
            print(f"{app}: {minutes} мин {sec} сек")


if __name__ == "__main__":
    main()