from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.schemas import DeviceCreate, DeviceRead
from app.service import create_device, get_device

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Distributed Device Service", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/devices", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create(payload: DeviceCreate, db: Session = Depends(get_db)) -> DeviceRead:
    return create_device(db, payload.name)


@app.get("/devices/{device_id}", response_model=DeviceRead)
def read(device_id: str, db: Session = Depends(get_db)) -> DeviceRead:
    device = get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
