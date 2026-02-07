from __future__ import annotations

import os
import sqlite3

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0.0")

DB_PATH = os.getenv("DB_PATH", "data/app.db")


def ensure_db() -> None:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup() -> None:
    ensure_db()


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool
    created_at: str


@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(db=Depends(get_db)):
    rows = db.execute(
        "SELECT id, title, done, created_at FROM tasks ORDER BY id DESC"
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


@app.post("/api/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db=Depends(get_db)):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    cursor = db.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
    db.commit()
    task_id = cursor.lastrowid
    row = db.execute(
        "SELECT id, title, done, created_at FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
    }


@app.put("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db=Depends(get_db)):
    row = db.execute(
        "SELECT id, title, done, created_at FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="task not found")

    new_title = row["title"]
    new_done = row["done"]

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="title is required")
        new_title = title
    if payload.done is not None:
        new_done = 1 if payload.done else 0

    db.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id),
    )
    db.commit()

    row = db.execute(
        "SELECT id, title, done, created_at FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
    }


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db=Depends(get_db)):
    cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="task not found")
    return {"status": "deleted"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")
