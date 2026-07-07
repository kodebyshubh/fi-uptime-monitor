from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

import db
from scheduler import start_scheduler, stop_scheduler

app = FastAPI(title="Uptime Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MonitorIn(BaseModel):
    url: HttpUrl


@app.on_event("startup")
def on_startup():
    db.init_db()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.post("/monitors", status_code=201)
def add_monitor(monitor: MonitorIn):
    try:
        monitor_id = db.create_monitor(str(monitor.url))
    except Exception:
        raise HTTPException(status_code=409, detail="URL already registered")
    return {"id": monitor_id, "url": str(monitor.url)}


@app.get("/monitors")
def get_monitors():
    return db.list_monitors()


@app.get("/monitors/{monitor_id}/checks")
def get_monitor_checks(monitor_id: int):
    return db.get_checks(monitor_id)


@app.delete("/monitors/{monitor_id}", status_code=204)
def remove_monitor(monitor_id: int):
    db.delete_monitor(monitor_id)
