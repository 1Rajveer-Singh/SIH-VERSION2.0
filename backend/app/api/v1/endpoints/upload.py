"""File upload endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.core.auth import get_current_active_user, require_engineer

router = APIRouter()

@router.post("/dem")
async def upload_dem(
    file: UploadFile = File(...),
    site_id: str = None,
    current_user = Depends(require_engineer)
):
    """Upload DEM file"""
    if not file.filename.endswith(('.tif', '.tiff')):
        raise HTTPException(400, "Only TIFF files supported")
    
    # Mock implementation - would upload to S3 and save metadata
    return {
        "message": "DEM file uploaded successfully",
        "filename": file.filename,
        "site_id": site_id,
        "size": file.size if hasattr(file, 'size') else 0
    }

@router.post("/drone")
async def upload_drone_image(
    file: UploadFile = File(...),
    site_id: str = None,
    current_user = Depends(require_engineer)
):
    """Upload drone imagery"""
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(400, "Only JPG/PNG files supported")
    
    return {
        "message": "Drone image uploaded successfully",
        "filename": file.filename,
        "site_id": site_id
    }