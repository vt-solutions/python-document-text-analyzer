"""
pro_batch.py
PRO-Feature: Batch-Verarbeitung mehrerer Dateien.
Verarbeitet eine Liste von Dateipfaden und gibt Ergebnisse als Dict zurück.
"""

import os
import threading
from typing import Callable


def process_batch(
    file_paths: list[str],
    allow_pro: bool,
    on_progress: Callable[[int, int, str], None] | None = None,
    on_done: Callable[[dict[str, str]], None] | None = None,
) -> None:
    """
    Verarbeitet alle Dateien in einem Hintergrundthread.

    on_progress(current, total, filename) – nach jeder Datei aufgerufen
    on_done(results)                      – am Ende mit Ergebnis-Dict aufgerufen
      results: {dateipfad: extrahierter_text_oder_fehlermeldung}
    """
    def _worker():
        from src.file_router import route_file
        results: dict[str, str] = {}
        total = len(file_paths)
        for i, path in enumerate(file_paths, 1):
            fname = os.path.basename(path)
            if on_progress:
                on_progress(i, total, fname)
            results[path] = route_file(path, allow_pro=allow_pro)
        if on_done:
            on_done(results)

    threading.Thread(target=_worker, daemon=True).start()


def combine_results(results: dict[str, str], separator: str = "\n\n") -> str:
    """
    Fasst alle Batch-Ergebnisse zu einem einzelnen Text zusammen.
    Jede Datei erhält eine Überschrift.
    """
    parts = []
    for path, text in results.items():
        fname = os.path.basename(path)
        parts.append(f"{'─' * 60}\n📄  {fname}\n{'─' * 60}\n{text}")
    return separator.join(parts)
