import time
import threading
import win32gui
import win32process
import psutil

from db import init_db, save_to_db
from idle import get_idle_seconds
from server import run_server, get_browser_status


IDLE_THRESHOLD = 60 # секунды простоя после которых не считаем время
BROWSER_PROCESSES = ("chrome.exe", "msedge.exe")

def getActiveWindowProcessName():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name()
    except Exception:
        return "Unknown"
    
def main():
    init_db() 

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Трекер запущен. Ctrl+C чтобі остановить и увидеть итоги.")

    time_per_app = {}
    check_interval = 1   # как часто проверяем активное окно в секундах
    save_interval = 10  # как часто пишем в базу в секундах
    seconds_since_save = 0

    try:
        while True:
            idle_seconds = get_idle_seconds()
            app_name = getActiveWindowProcessName()

            domain, audible = (None, False)
            if app_name in BROWSER_PROCESSES:
                domain, audible = get_browser_status()

            # либо были недавние мышь/клава, либо играет звук в браузере
            user_present = (idle_seconds < IDLE_THRESHOLD) or audible

            if user_present:
                if app_name in BROWSER_PROCESSES and domain:
                    activity_name = domain # считаем сайт
                else:
                    activity_name = app_name # обычная программа

                time_per_app[activity_name] = time_per_app.get(activity_name, 0) + check_interval

                if audible and idle_seconds >= IDLE_THRESHOLD:
                    print(f"[звук играет, не простой] {activity_name}")
            else:
                print(f"[простой {int(idle_seconds)} сек] время не считается")

            time.sleep(check_interval)

            seconds_since_save += check_interval
            if seconds_since_save >= save_interval:
                save_to_db(time_per_app)
                print(f"[сохранено в базу] {time_per_app}")
                time_per_app = {}
                seconds_since_save = 0

    except KeyboardInterrupt:
        save_to_db(time_per_app)
        print("\n--- Сессия сохранена в базу данных ---")


if __name__ == "__main__":
    main()