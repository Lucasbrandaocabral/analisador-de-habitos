"""
Automatic collection scheduler.

Runs collect_and_store() every INTERVAL_MINUTES minutes in a background loop.
Designed to be started alongside the FastAPI server.

Usage:
    python scheduler.py              # default: every 15 minutes
    python scheduler.py --interval 5 # every 5 minutes
"""

import time
import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal, init_db
from app.services.collector import collect_and_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [scheduler] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def run(interval_minutes: int = 15) -> None:
    init_db()
    log.info(f"Scheduler iniciado — coletando a cada {interval_minutes} min.")

    while True:
        try:
            db = SessionLocal()
            result = collect_and_store(db)
            db.close()
            log.info(
                f"Coleta concluída: {result['inserted']} novos registros, "
                f"{result['skipped']} duplicados, fonte={result['source']}"
            )
        except Exception as exc:
            log.error(f"Erro na coleta: {exc}")

        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Habit data collector scheduler")
    parser.add_argument("--interval", type=int, default=15, help="Intervalo em minutos")
    args = parser.parse_args()
    run(args.interval)
