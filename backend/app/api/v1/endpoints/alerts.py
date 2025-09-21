"""Alert endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_active_user
from app.core.database import get_database
from typing import List, Optional

router = APIRouter()

@router.get("/")
async def get_alerts(
    site_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    current_user = Depends(get_current_active_user)
):
    """Get alerts with filtering"""
    db = get_database()
    query = {}
    if site_id:
        query["site_id"] = site_id
    if status:
        query["status"] = status
    
    alerts = await db["alerts"].find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
    return [{"id": str(a["_id"]), **{k: v for k, v in a.items() if k != "_id"}} for a in alerts]

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, current_user = Depends(get_current_active_user)):
    """Acknowledge an alert"""
    from datetime import datetime
    from bson import ObjectId
    
    db = get_database()
    result = await db["alerts"].update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": {"status": "acknowledged", "acknowledged_by": current_user.id, "acknowledged_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Alert not found")
    return {"message": "Alert acknowledged"}