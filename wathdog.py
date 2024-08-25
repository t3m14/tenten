import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f'Перезагрузка... {event.src_path}')
            os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    path = "."  # Путь к вашему проекту
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        subprocess.run([sys.executable, 'bot.py'])  # Замените на имя вашего файла с ботом
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

