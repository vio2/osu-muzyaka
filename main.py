import keyboard as kb
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from utils import get_or_create_config, update_and_save_config


class ReplayHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".osr"):
            print(f"got new replay: {event.src_path}")

            try:
                os.startfile(event.src_path)
                print("sent to osu!")
            except Exception as e:
                print(f"error! {e}")


config = get_or_create_config()


def main():
    event_handler = ReplayHandler()
    observer = Observer()
    observer.schedule(event_handler, config.replays_path, recursive=False)
    print(f"im watching {config.replays_path} now.")
    print("press ctrl+c to exit.")

    observer.start()

    try:
        while (True):
            time.sleep(.1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    print("Hello.")
    print(
        f"current settings:\nosu directory: {config.osu_path}\nparsing delay: {config.delay}")
    if input("would you like to change this? (y/n)\n") == 'y':
        new_path = input("enter osu! path: ")
        new_delay = input("enter new delay in milliseconds: ")
        if new_path:
            config = update_and_save_config(config, osu_path=new_path)
        if new_delay:
            config = update_and_save_config(config, delay=new_delay)
        print("okay, changes saved.")
        main()
    else:
        print("no")
