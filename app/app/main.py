"""Tasks API - a small REST API used to practise containers and CI/CD.

Interactive docs: http://localhost:8000/docs
"""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Task, TaskCreate, TaskOut, TaskUpdate

APP_VERSION = os.getenv("APP_VERSION", "dev")  # set to the git commit SHA by CI


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables on startup if missing
    yield


app = FastAPI(title="Homelab Tasks API", version=APP_VERSION, lifespan=lifespan)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Used by Docker healthcheck and Uptime Kuma. Also checks the database."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as err:
        raise HTTPException(status_code=503, detail="database unavailable") from err
    return {"status": "ok", "version": APP_VERSION}


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.scalars(select(Task).order_by(Task.id)).all()


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(title=payload.title)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def _get_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, task_id)


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    db.delete(task)
    db.commit()
