from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import PermissionCreate, PermissionOut
from app.database import get_db
from app.auth import get_current_active_user
from app.models import User, EventPermission, Event  # Make sure these are imported
from typing import List

router = APIRouter()

def has_permission(db: Session, user_id: int, event_id: int, required_role: str):
    permission = db.query(EventPermission).filter(
        EventPermission.user_id == user_id,
        EventPermission.event_id == event_id
    ).first()
    
    if not permission:
        return False
    
    role_hierarchy = {"viewer": 0, "editor": 1, "owner": 2}
    return role_hierarchy[permission.role] >= role_hierarchy[required_role]

@router.post("/{event_id}/share", response_model=PermissionOut)
def share_event(
    event_id: int,
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if current user has owner rights
    if not has_permission(db, current_user.id, event_id, "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user exists
    user = db.query(User).filter(User.id == permission.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if permission already exists
    existing = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == permission.user_id
    ).first()
    
    if existing:
        existing.role = permission.role
    else:
        existing = EventPermission(
            event_id=event_id,
            user_id=permission.user_id,
            role=permission.role
        )
        db.add(existing)
    
    db.commit()
    db.refresh(existing)
    return existing

@router.get("/{event_id}/permissions", response_model=List[PermissionOut])
def list_permissions(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not has_permission(db, current_user.id, event_id, "viewer"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return db.query(EventPermission).filter(
        EventPermission.event_id == event_id
    ).all()

@router.put("/{event_id}/permissions/{user_id}", response_model=PermissionOut)
def update_permission(
    event_id: int,
    user_id: int,
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not has_permission(db, current_user.id, event_id, "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_permission = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == user_id
    ).first()
    
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db_permission.role = permission.role
    db.commit()
    db.refresh(db_permission)
    return db_permission

@router.delete("/{event_id}/permissions/{user_id}")
def remove_permission(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not has_permission(db, current_user.id, event_id, "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove your own owner permissions")
    
    db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == user_id
    ).delete()
    db.commit()
    return {"message": "Permission removed"}