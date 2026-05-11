"""Scheduler ligero para avanzar la cola musical automaticamente."""

import os
import sys
import threading
import time

from django.core.cache import cache


_scheduler_started = False


def _debe_iniciar_scheduler():
    if "test" in sys.argv:
        return False
    if os.environ.get("RUN_MAIN") not in {"true", "True", "1", None}:
        return False
    return True


def iniciar_scheduler_musical():
    global _scheduler_started
    if _scheduler_started or not _debe_iniciar_scheduler():
        return
    _scheduler_started = True

    def worker():
        from bongusto.modules.musica.services import MusicaService

        service = MusicaService()
        while True:
            try:
                if cache.add("bongusto.music.scheduler.tick", "1", timeout=8):
                    try:
                        service.sincronizar_reproduccion()
                    finally:
                        cache.delete("bongusto.music.scheduler.tick")
            except Exception:
                pass
            time.sleep(5)

    thread = threading.Thread(target=worker, name="bongusto-music-scheduler", daemon=True)
    thread.start()


__all__ = ["iniciar_scheduler_musical"]
