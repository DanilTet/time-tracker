import time
import win32gui
import win32process
import psutil

from db import init_db, save_to_db

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
    print("Трекер запущен. Ctrl+C чтобі остановить и увидеть итоги.")

    time_per_app = {}
    check_interval = 1   # как часто проверяем активное окно в секундах
    save_interval = 10  # как часто пишем в базу в секундах
    seconds_since_save = 0
    try:
        while True:
            app_name = getActiveWindowProcessName()
            time_per_app[app_name] = time_per_app.get(app_name, 0) + check_interval
            time.sleep(check_interval)

            seconds_since_save += check_interval
            if seconds_since_save >= save_interval:
                save_to_db(time_per_app)
                print(f"[сохранено в базу] {time_per_app}")
                time_per_app = {}
                seconds_since_save = 0

    except KeyboardInterrupt:
        save_to_db(time_per_app)  # сохраняем время которое не успело дойти до 60 сек
        print("\n--- Сессия сохранена в базу данных ---")


if __name__ == "__main__":
    main()