"""Basic endpoints for sites, alerts, users, upload, and dashboard"""

# sites.py
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_active_user
from app.core.database import get_database
import logging

router = APIRouter()

@router.get("/")
async def get_sites(current_user = Depends(get_current_active_user)):
    """Get all sites"""
    db = get_database()
    sites = await db["sites"].find({}).to_list(length=None)
    return [{"id": str(s["_id"]), **{k: v for k, v in s.items() if k != "_id"}} for s in sites]

@router.get("/{site_id}")
async def get_site(site_id: str, current_user = Depends(get_current_active_user)):
    """Get specific site"""
    db = get_database()
    site = await db["sites"].find_one({"site_id": site_id})
    if not site:
        raise HTTPException(404, "Site not found")
    return {"id": str(site["_id"]), **{k: v for k, v in site.items() if k != "_id"}}