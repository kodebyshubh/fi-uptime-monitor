import asyncio
import os
import time

import httpx

import db

CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", "30"))

_task: asyncio.Task | None = None


async def _check_one(client: httpx.AsyncClient, monitor: dict):
    start = time.monotonic()
    try:
        resp = await client.get(monitor["url"], timeout=5.0, follow_redirects=True)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        is_up = 200 <= resp.status_code < 400
        db.insert_check(monitor["id"], resp.status_code, elapsed_ms, is_up)
    except httpx.HTTPError:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        db.insert_check(monitor["id"], None, elapsed_ms, False)


async def _run_loop():
    async with httpx.AsyncClient() as client:
        while True:
            monitors = db.list_monitor_urls()
            if monitors:
                await asyncio.gather(*(_check_one(client, m) for m in monitors))
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)


def start_scheduler():
    global _task
    _task = asyncio.create_task(_run_loop())


def stop_scheduler():
    if _task:
        _task.cancel()
