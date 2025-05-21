from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ChangeOut, DiffOut
from app.database import get_db
from app.auth import get_current_active_user
from app.models import User, EventChange, Event, EventPermission  # Add User and EventPermission here
from typing import List

router = APIRouter()

# ... rest of your history.py code remains the same ...

@router.get("/{event_id}/history", response_model=List[ChangeOut])
def get_event_history(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user has permission to view the event
    event = db.query(Event).join(Event.permissions).filter(
        Event.id == event_id,
        EventPermission.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or no access")
    
    return db.query(EventChange).filter(
        EventChange.event_id == event_id
    ).order_by(EventChange.version).all()

@router.get("/{event_id}/history/{version_id}", response_model=ChangeOut)
def get_event_version(
    event_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user has permission to view the event
    event = db.query(Event).join(Event.permissions).filter(
        Event.id == event_id,
        EventPermission.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or no access")
    
    change = db.query(EventChange).filter(
        EventChange.event_id == event_id,
        EventChange.version == version_id
    ).first()
    
    if not change:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return change

@router.post("/{event_id}/rollback/{version_id}", response_model=ChangeOut)
def rollback_event_version(
    event_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user has permission to edit the event
    event = db.query(Event).join(Event.permissions).filter(
        Event.id == event_id,
        EventPermission.user_id == current_user.id,
        EventPermission.role.in_(["owner", "editor"])
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or no edit access")
    
    target_change = db.query(EventChange).filter(
        EventChange.event_id == event_id,
        EventChange.version == version_id
    ).first()
    
    if not target_change:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Create a new change record for the rollback
    rollback_change = EventChange(
        event_id=event_id,
        user_id=current_user.id,
        version=None,  # Will be auto-incremented
        change_type="rollback",
        changes={
            "rolled_back_from": target_change.version,
            "changes": target_change.changes
        }
    )
    db.add(rollback_change)
    
    # Apply the changes from the target version
    for field, values in target_change.changes.items():
        if field in ["old", "new"]:  # Handle diff format
            for subfield, subvalue in values.items():
                setattr(event, subfield, subvalue)
        else:
            setattr(event, field, values["new"] if "new" in values else values)
    
    db.commit()
    db.refresh(rollback_change)
    return rollback_change

@router.get("/{event_id}/diff/{version_id1}/{version_id2}", response_model=DiffOut)
def get_diff_between_versions(
    event_id: int,
    version_id1: int,
    version_id2: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user has permission to view the event
    event = db.query(Event).join(Event.permissions).filter(
        Event.id == event_id,
        EventPermission.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or no access")
    
    version1 = db.query(EventChange).filter(
        EventChange.event_id == event_id,
        EventChange.version == version_id1
    ).first()
    
    version2 = db.query(EventChange).filter(
        EventChange.event_id == event_id,
        EventChange.version == version_id2
    ).first()
    
    if not version1 or not version2:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    # Simple diff implementation - in a real app you might want a more sophisticated diff
    diff = {}
    changes1 = version1.changes
    changes2 = version2.changes
    
    all_keys = set(changes1.keys()).union(set(changes2.keys()))
    for key in all_keys:
        val1 = changes1.get(key, {}).get("new") if isinstance(changes1.get(key), dict) else changes1.get(key)
        val2 = changes2.get(key, {}).get("new") if isinstance(changes2.get(key), dict) else changes2.get(key)
        if val1 != val2:
            diff[key] = {"version1": val1, "version2": val2}
    
    return {
        "version1": version_id1,
        "version2": version_id2,
        "differences": diff
    }