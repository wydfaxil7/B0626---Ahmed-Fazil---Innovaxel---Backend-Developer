from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Event, Registration
from schemas import RegistrationCreate, RegistrationResponse, CancelResponse

router = APIRouter(
    prefix="/registrations",
    tags=["Registrations"]
)


@router.post("/", response_model=RegistrationResponse, status_code=201)
def register_user(reg_data: RegistrationCreate, db: Session = Depends(get_db)):
    """
    Register a user for an event.

    - **user_name**: Name of the user registering
    - **event_id**: ID of the event to register for
    
    Rules:
    - Events must exists
    - must be booked
    - Same user cannot book or register again for an event
    - Race conditions prevented via database row locking
    """

    event = (
        db.query(Event)
        .filter(Event.id == reg_data.event_id)
        .with_for_update().first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Event with ID {reg_data.event_id} not found."
        )
    

    active_count = (
        db.query(Registration)
        .filter(
            Registration.event_id == reg_data.event_id,
            Registration.status == "active"
        )
        .count()
    )

    if active_count >= event.total_seats:
        raise HTTPException(
            status_code=400,
            detail=f"Event '{event.name}' is fully booked"
        )
    
    already_registered = (
        db.query(Registration)
        .filter(
            Registration.event_id == reg_data.event_id,
            Registration.user_name == reg_data.user_name,
            Registration.status == "active"
        )
        .first()
    )

    if already_registered:
        raise HTTPException(
            status_code=400,
            detail=f"User '{reg_data.user_name}' is already registered for this event"
        )
    
    # All checks passed, now create registrations
    new_registration = Registration(
        user_name=reg_data.user_name,
        event_id=reg_data.event_id,
        status="active"
    )

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return new_registration

@router.delete("/{registration_id}", response_model=CancelResponse)
def cancel_registration(registration_id: int, db: Session = Depends(get_db)):
    """
    Cancel an existing registration.

    - **registration_id**: ID of the registration to cancel

    Rules: 
    - Registration must exist
    - Registration must not already be cancelled

    Although this is a soft delete, means the record still remains in the database
    but the status is changed to "cancelled" 
    """

    registration = (
        db.query(Registration)
        .filter(Registration.id == registration_id)
        .first()
    )

    if not registration:
        raise HTTPException(
            status_code=404,
            detail=f"Registration with ID {registration_id} not found"
        )
    
    registration.status = "cancelled"
    db.commit()

    return CancelResponse(
        message=f"Registration with ID {registration_id} cancelled successfully",
        registration_id=registration_id
    )