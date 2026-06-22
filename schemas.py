from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Literal


class EventCreate(BaseModel):
    name: str = Field(..., min_length=1)
    total_seats: int = Field(..., gt=0)
    event_date: datetime

    # Validator: to ensure event date must be in the future
    @field_validator("event_date")
    @classmethod
    def date_must_be_future(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError("Event datemust be in the future")
        return v
    

class EventResponse(BaseModel):
    id: int
    name: str
    total_seats: int
    event_date: datetime
    created_date: datetime
    available_seats: int
    total_registrations: int

    model_config = {"from_attributes": True}


class RegistrationCreate(BaseModel):
    user_name: str = Field(..., min_length=1)
    event_id: int


class RegistrationResponse(BaseModel):
    id: int
    user_name: str
    event_id: int
    registered_at: datetime
    status: Literal["active", "cancelled"]

    model_config = {"from_attributes": True}


class CancelResponse(BaseModel):
    message: str
    registration_id: id
