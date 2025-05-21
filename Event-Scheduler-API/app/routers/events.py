from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.schemas import EventCreate, EventUpdate, EventOut, BatchEventCreate
from app.database import get_db
from app.auth import get_current_active_user
from app.models import User, Event, EventPermission  # Add these imports
from app.services.event_service import (
    create_event,
    get_events,
    get_event,
    update_event,
    delete_event,
    create_batch_events,
    check_event_conflict,
    has_permission,  # Add this if missing
    record_change  # Add this if missing
)
from app.database import get_db
from app.auth import get_current_active_user
from app.models import User, Event

router = APIRouter()

@router.post("/", response_model=EventOut)
def create_new_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check for conflicts
    if check_event_conflict(db, current_user.id, event.start_time, event.end_time):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event conflicts with existing events"
        )
    return create_event(db=db, event=event, user_id=current_user.id)

@router.get("/", response_model=List[EventOut])
def list_events(
    skip: int = 0,
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_events(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{event_id}", response_model=EventOut)
def read_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    event = get_event(db, event_id=event_id, user_id=current_user.id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=EventOut)
def update_existing_event(
    event_id: int,
    event: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_event = get_event(db, event_id=event_id, user_id=current_user.id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if not has_permission(db, current_user.id, event_id, "editor"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return update_event(db=db, event_id=event_id, event=event, user_id=current_user.id)

@router.delete("/{event_id}")
def delete_existing_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_event = get_event(db, event_id=event_id, user_id=current_user.id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Only owner can delete
    if not has_permission(db, current_user.id, event_id, "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    delete_event(db=db, event_id=event_id, user_id=current_user.id)
    return {"message": "Event deleted successfully"}

@router.post("/batch", response_model=List[EventOut])
def create_multiple_events(
    events: BatchEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return create_batch_events(db=db, events=events.events, user_id=current_user.id)