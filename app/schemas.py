from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    category: str
    starts_at: datetime
    ends_at: datetime | None
    venue: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    price_text: str | None
    image_url: str | None
    source_name: str
    source_key: str
    source_url: str
    status: str
    is_sponsored: bool


class ReviewIn(BaseModel):
    status: str = Field(pattern="^(published|rejected|pending)$")


class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    description: str | None = None
    category: str = "otros"
    starts_at: datetime
    ends_at: datetime | None = None
    venue: str | None = None
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    price_text: str | None = None
    image_url: str | None = None
    source_name: str = "Añadido manualmente"
    source_key: str = "manual"
    source_url: str
