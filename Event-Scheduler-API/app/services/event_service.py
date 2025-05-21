from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Event, EventChange, EventPermission
from app.schemas import EventCreate, EventUpdate
from typing import List
from typing import Dict

def create_event(db: Session, event: EventCreate, user_id: int):
    db_event = Event(
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        is_recurring=event.is_recurring,
        recurrence_pattern=event.recurrence_pattern,
        created_by=user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Add owner permission
    add_permission(db, user_id, db_event.id, "owner")
    
    # Record creation in history
    record_change(
        db,
        db_event.id,
        user_id,
        "create",
        {},
        event.dict()
    )
    
    return db_event

def record_change(db: Session, event_id: int, user_id: int, change_type: str, old_values: dict, new_values: dict):
    # Get next version number
    last_version = db.query(EventChange.version).filter(
        EventChange.event_id == event_id
    ).order_by(EventChange.version.desc()).first()
    
    next_version = 1 if last_version is None else last_version[0] + 1
    
    # Calculate diff
    diff = {}
    for key in new_values:
        if key in old_values and old_values[key] != new_values[key]:
            diff[key] = {"old": old_values[key], "new": new_values[key]}
        elif key not in old_values:
            diff[key] = {"old": None, "new": new_values[key]}
    
    # For deletions, track what was removed
    if change_type == "delete":
        diff = old_values
    
    db_change = EventChange(
        event_id=event_id,
        user_id=user_id,
        version=next_version,
        change_type=change_type,
        changes=diff
    )
    db.add(db_change)
    db.commit()

# Add this function to your event_service.py
def has_permission(db: Session, user_id: int, event_id: int, required_role: str):
    permission = db.query(EventPermission).filter(
        EventPermission.user_id == user_id,
        EventPermission.event_id == event_id
    ).first()
    
    if not permission:
        return False
    
    role_hierarchy = {"viewer": 0, "editor": 1, "owner": 2}
    return role_hierarchy[permission.role] >= role_hierarchy[required_role]

def get_events(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None
):
    query = db.query(Event).join(EventPermission).filter(
        EventPermission.user_id == user_id
    )
    
    if start_date:
        query = query.filter(Event.start_time >= start_date)
    if end_date:
        query = query.filter(Event.end_time <= end_date)
    
    return query.offset(skip).limit(limit).all()

def get_event(db: Session, event_id: int, user_id: int):
    return db.query(Event).join(EventPermission).filter(
        Event.id == event_id,
        EventPermission.user_id == user_id
    ).first()

def update_event(db: Session, event_id: int, event: EventUpdate, user_id: int):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    
    # Get original values for history
    original_values = {
        "title": db_event.title,
        "description": db_event.description,
        "start_time": db_event.start_time,
        "end_time": db_event.end_time,
        "location": db_event.location,
        "is_recurring": db_event.is_recurring,
        "recurrence_pattern": db_event.recurrence_pattern
    }
    
    # Update fields
    for field, value in event.dict(exclude_unset=True).items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    
    # Record update in history
    record_change(
        db,
        event_id,
        user_id,
        "update",
        original_values,
        event.dict(exclude_unset=True)
    )
    
    return db_event

def delete_event(db: Session, event_id: int, user_id: int):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        # Record deletion in history
        record_change(
            db,
            event_id,
            user_id,
            "delete",
            {
                "title": db_event.title,
                "description": db_event.description,
                "start_time": db_event.start_time,
                "end_time": db_event.end_time
            },
            {}
        )
        
        # Delete permissions first
        db.query(EventPermission).filter(EventPermission.event_id == event_id).delete()
        
        # Then delete the event
        db.delete(db_event)
        db.commit()

def create_batch_events(db: Session, events: List[EventCreate], user_id: int):
    created_events = []
    for event in events:
        created_events.append(create_event(db, event, user_id))
    return created_events

def check_event_conflict(db: Session, user_id: int, start_time: datetime, end_time: datetime):
    conflicting_events = db.query(Event).join(EventPermission).filter(
        EventPermission.user_id == user_id,
        Event.start_time < end_time,
        Event.end_time > start_time
    ).count()
    
    return conflicting_events > 0

def record_change(db: Session, event_id: int, user_id: int, change_type: str, old_values: dict, new_values: dict):
    # Get next version number
    last_version = db.query(EventChange.version).filter(
        EventChange.event_id == event_id
    ).order_by(EventChange.version.desc()).first()
    
    next_version = 1 if last_version is None else last_version[0] + 1
    
    # Calculate diff
    diff = {}
    for key in new_values:
        if key in old_values and old_values[key] != new_values[key]:
            diff[key] = {"old": old_values[key], "new": new_values[key]}
        elif key not in old_values:
            diff[key] = {"old": None, "new": new_values[key]}
    
    # For deletions, track what was removed
    if change_type == "delete":
        diff = old_values
    
    db_change = EventChange(
        event_id=event_id,
        user_id=user_id,
        version=next_version,
        change_type=change_type,
        changes=diff
    )
    db.add(db_change)
    db.commit()