from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.models.message import DirectMessage
from app.models.user import User
from app.dependencies.auth import get_current_user
from sqlalchemy import or_, and_

router = APIRouter(prefix="/messages", tags=["Messages"])

class SendMessageRequest(BaseModel):
    receiver_id: int
    content: str

@router.get("/users")
def get_messageable_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), q: str = ""):
    """Get list of users that the current user can message (search by name or company)"""
    query = db.query(User).filter(User.id != current_user.id)
    if q:
        query = query.filter(or_(User.name.ilike(f"%{q}%"), User.company_name.ilike(f"%{q}%")))
    users = query.limit(20).all()
    
    result = []
    for u in users:
        u_role = u.role.value if hasattr(u.role, 'value') else u.role
        display_name = u.company_name if (u_role == 'hr' and u.company_name) else u.name
        result.append({
            "id": u.id,
            "name": u.name,
            "display_name": display_name,
            "role": u_role,
            "title": u.title,
            "company_name": u.company_name,
            "avatar_url": u.avatar_url
        })
    return result

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: str
    sender_name: str | None = None
    receiver_name: str | None = None

    class Config:
        from_attributes = True

@router.get("/conversations")
def get_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get list of users that the current user has messages with"""
    # Find all unique user IDs that current user has communicated with
    sent = db.query(DirectMessage.receiver_id).filter(DirectMessage.sender_id == current_user.id).distinct().all()
    received = db.query(DirectMessage.sender_id).filter(DirectMessage.receiver_id == current_user.id).distinct().all()
    
    partner_ids = set([r[0] for r in sent] + [r[0] for r in received])
    
    conversations = []
    for pid in partner_ids:
        partner = db.query(User).filter(User.id == pid).first()
        if not partner:
            continue
        
        # Get latest message
        latest = db.query(DirectMessage).filter(
            or_(
                and_(DirectMessage.sender_id == current_user.id, DirectMessage.receiver_id == pid),
                and_(DirectMessage.sender_id == pid, DirectMessage.receiver_id == current_user.id)
            )
        ).order_by(DirectMessage.created_at.desc()).first()
        
        # Count unread
        unread = db.query(DirectMessage).filter(
            DirectMessage.sender_id == pid,
            DirectMessage.receiver_id == current_user.id,
            DirectMessage.is_read == False
        ).count()
        
        partner_role = partner.role.value if hasattr(partner.role, 'value') else partner.role
        display_name = partner.company_name if (partner_role == 'hr' and partner.company_name) else partner.name
        
        conversations.append({
            "user_id": partner.id,
            "name": partner.name,
            "display_name": display_name,
            "email": partner.email,
            "role": partner_role,
            "title": partner.title,
            "company_name": partner.company_name,
            "avatar_url": partner.avatar_url,
            "last_message": latest.content if latest else "",
            "last_message_time": str(latest.created_at) if latest else "",
            "unread": unread
        })
    
    # Sort by latest message time
    conversations.sort(key=lambda x: x["last_message_time"], reverse=True)
    return conversations

@router.get("/history/{partner_id}")
def get_message_history(partner_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get message history with a specific user"""
    messages = db.query(DirectMessage).filter(
        or_(
            and_(DirectMessage.sender_id == current_user.id, DirectMessage.receiver_id == partner_id),
            and_(DirectMessage.sender_id == partner_id, DirectMessage.receiver_id == current_user.id)
        )
    ).order_by(DirectMessage.created_at.asc()).limit(100).all()
    
    # Mark unread messages as read
    db.query(DirectMessage).filter(
        DirectMessage.sender_id == partner_id,
        DirectMessage.receiver_id == current_user.id,
        DirectMessage.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    result = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        sender_role = sender.role.value if sender and hasattr(sender.role, 'value') else (sender.role if sender else 'candidate')
        sender_display = (sender.company_name if (sender_role == 'hr' and sender.company_name) else sender.name) if sender else "Unknown"
        result.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "is_read": m.is_read,
            "created_at": str(m.created_at),
            "sender_name": sender.name if sender else "Unknown",
            "sender_display_name": sender_display,
            "sender_role": sender_role,
            "sender_company": sender.company_name if sender else None
        })
    
    return result

@router.post("/send")
async def send_message(req: SendMessageRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Send a direct message"""
    receiver = db.query(User).filter(User.id == req.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    msg = DirectMessage(
        sender_id=current_user.id,
        receiver_id=req.receiver_id,
        content=req.content
    )
    db.add(msg)
    
    # Calculate display name for sender
    sender_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    display_name = current_user.company_name if (sender_role == 'hr' and current_user.company_name) else current_user.name

    # Also create a Notification for the receiver
    from app.models.notification import Notification
    notification = Notification(
        user_id=req.receiver_id,
        title=f"New message from {display_name}",
        message=req.content[:50] + "..." if len(req.content) > 50 else req.content
    )
    db.add(notification)
    
    db.commit()
    db.refresh(msg)
    
    # Push CHAT_MESSAGE to receiver via WebSocket
    from app.routes.ws import manager
    chat_payload = {
        "type": "CHAT_MESSAGE",
        "message_id": msg.id,
        "sender_id": current_user.id,
        "sender_name": display_name,
        "content": req.content,
        "created_at": str(msg.created_at)
    }
    await manager.send_personal_message(message=chat_payload, user_id=req.receiver_id)
    
    # Also push a NOTIFICATION event to receiver so the bell icon updates
    await manager.send_personal_message(
        message={
            "type": "NOTIFICATION",
            "title": f"New message from {display_name}",
            "message": req.content[:50] + "..." if len(req.content) > 50 else req.content
        },
        user_id=req.receiver_id
    )
    
    # Push a lightweight event to the SENDER so their conversation list refreshes
    await manager.send_personal_message(
        message={
            "type": "CONVERSATION_UPDATE",
            "partner_id": req.receiver_id,
            "last_message": req.content,
            "created_at": str(msg.created_at)
        },
        user_id=current_user.id
    )
    
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "created_at": str(msg.created_at)
    }
