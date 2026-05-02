"""
Convenience launcher: starts both the FastAPI server and the scheduler
in separate threads so a single `python run.py` is enough.
"""

import threading
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_api():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


def start_scheduler(interval: int = 15):
    from scheduler import run
    run(interval_minutes=interval)


if __name__ == "__main__":
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 15

    scheduler_thread = threading.Thread(target=start_scheduler, args=(interval,), daemon=True)
    scheduler_thread.start()

    start_api()
