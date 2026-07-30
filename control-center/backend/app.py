"""Bot Control Center — FastAPI backend.

Read API over control.db + ingest refresh. Job endpoints are added by the
job_runner phase. Runs LOCALLY (it later spawns the `claude` CLI + reaches secrets)."""
from __future__ import annotations
import subprocess
import threading
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import queries
from config import BACKEND_DIR, CC_DIR, PY
from db import init_db

app = FastAPI(title="Bot Control Center", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"], allow_headers=["*"],
)

_ingest_lock = threading.Lock()
_ingest_state = {"running": False, "last": None}


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True, "ingest": _ingest_state}


@app.get("/api/stats")
def stats():
    return queries.stats()


@app.get("/api/bots")
def bots():
    return queries.list_bots()


@app.get("/api/bots/{target_id}")
def bot(target_id: str):
    b = queries.get_bot(target_id)
    if not b:
        raise HTTPException(404, "unknown bot")
    return b


@app.get("/api/issues")
def issues(status: str = Query(None), bot: str = Query(None),
           owner: str = Query(None), priority: str = Query(None)):
    return queries.list_issues(status, bot, owner, priority)


@app.get("/api/scenarios")
def scenarios(agent: str = Query(None)):
    return queries.list_scenarios(agent)


@app.get("/api/test-matrix")
def test_matrix():
    return queries.test_matrix()


@app.get("/api/deploys")
def deploys():
    return queries.list_table("deploys", order="ts DESC")


@app.get("/api/fixes")
def fixes():
    return queries.list_table("fixes", order="date DESC")


@app.get("/api/versions")
def versions():
    return queries.list_table("versions", order="ts DESC")


def _do_ingest(mode: str):
    try:
        subprocess.run([PY, "-m", "ingest", mode], cwd=str(BACKEND_DIR),
                       capture_output=True, text=True, timeout=300)
    finally:
        with _ingest_lock:
            _ingest_state.update(running=False, last=mode)


@app.post("/api/ingest/refresh")
def ingest_refresh(mode: str = Query("--all")):
    with _ingest_lock:
        if _ingest_state["running"]:
            return {"queued": False, "reason": "already running"}
        _ingest_state["running"] = True
    threading.Thread(target=_do_ingest, args=(mode,), daemon=True).start()
    return {"queued": True, "mode": mode}


# Serve the cockpit (mounted last so /api/* routes win). Same-origin -> no CORS needed.
_frontend = CC_DIR / "frontend"
if _frontend.exists():
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="cockpit")
