import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path to import train
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from train import train

class DataChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("creditcard_clean.csv"):
            print(f"Modification détectée sur {event.src_path}. Lancement du réentraînement...")
            try:
                train()
                print("Réentraînement terminé avec succès.")
            except Exception as e:
                print(f"Erreur lors du réentraînement : {e}")

if __name__ == "__main__":
    # Chemin vers le dossier contenant les données
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "notebooks")
    event_handler = DataChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, data_dir, recursive=False)
    observer.start()
    print(f"Surveillance du dossier : {data_dir}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()