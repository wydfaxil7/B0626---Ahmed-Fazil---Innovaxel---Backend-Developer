from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Event, Registration
from schemas import EventCreate, EventResponse
from datetime import datetime,timezone

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

def build_event_response(event: Event) -> EventResponse:
    
    active_registrations = [
        r for r in event.registrations if r.status == "active" 
    ]
    total_registrations = len(active_registrations)
    available_seats = event.total_seats - total_registrations

    return EventResponse(
        id=event.id,
        name=event.name,
        total_seats=event.total_seats,
        event_date=event.event_date,
        created_at=event.created_at,
        available_seats=available_seats,
        total_registrations=total_registrations
    )


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(
    event_data: EventCreate, 
    db: Session = Depends(get_db)
):

    """
    Create a new event.

    - **name**: Must be unique
    - **total_seats**: Must be greater than 0
    - **event_date**: Must be in the future
    """

    existing = db.query(Event).filter(Event.name == event_data.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Event with name '{event_data.name}' already exists."
        )

    stripped_date = event_data.event_date.replace(tzinfo=None)

    new_event = Event(
        name=event_data.name,
        total_seats=event_data.total_seats,
        event_date=stripped_date
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return build_event_response(new_event)


@router.get("/", response_model=list[EventResponse])
def get_events(
    upcoming_only: bool = Query(False, description="Filter to show only future events"),
    db: Session = Depends(get_db)
):

    """
    Retrieve all events sorted by date.

    - **upcoming_only**: If true, returns only future events
    """

    query = db.query(Event)

    if upcoming_only:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        query = query.filter(Event.event_date > now)

    events = query.order_by(Event.event_date.asc()).all()

    return [build_event_response(event) for event in events]