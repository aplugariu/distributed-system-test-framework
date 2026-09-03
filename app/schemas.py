from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import DeviceStatus


class DeviceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: DeviceStatus
    created_at: datetime
