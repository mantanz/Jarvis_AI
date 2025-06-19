import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from processing import load_documents, split_documents, add_to_chroma

DATA_PATH = "data"

class PDFChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".pdf"):
            print(f"New PDF detected: {event.src_path}")
            self.ingest()

    def on_modified(self, event):
        if event.src_path.endswith(".pdf"):
            print(f"PDF modified: {event.src_path}")
            self.ingest()

    def ingest(self):
        documents = load_documents()
        chunks = split_documents(documents)
        add_to_chroma(chunks)
        print("Ingestion done!")

if __name__ == "__main__":
    event_handler = PDFChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DATA_PATH, recursive=False)
    observer.start()
    print(f"Watching folder: {DATA_PATH}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
