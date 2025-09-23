"""
Model Training API Router
Handles ML model training, monitoring, and deployment operations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
import uuid
import numpy as np
from datetime import datetime, timedelta
import logging

from ..database.connection import get_database
from ..models.training import (
    TrainingConfigRequest, 
    TrainingJob, 
    TrainingStatusResponse,
    TrainingMetrics,
    ModelDeploymentRequest,
    ModelPerformanceReport
)
from .auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for active training jobs (in production, use Redis)
active_training_jobs: Dict[str, Dict[str, Any]] = {}


async def simulate_model_training(
    job_id: str, 
    config: TrainingConfigRequest, 
    user_id: str,
    db
):
    """
    Simulate the multi-modal model training process
    In production, this would interface with actual ML training pipelines
    """
    try:
        # Update job status to preparing
        await db.training_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "preparing",
                    "started_at": datetime.utcnow(),
                    "logs": ["Initializing multi-modal training pipeline...", 
                            "Loading training datasets...",
                            "Preparing model architectures..."]
                }
            }
        )
        
        # Simulate preparation time
        await asyncio.sleep(2)
        
        # Update to training status
        await db.training_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "training",
                    "estimated_completion": datetime.utcnow() + timedelta(minutes=5)
                },
                "$push": {
                    "logs": "Starting multi-modal training..."
                }
            }
        )
        
        total_epochs = config.hyperparameters.get("epochs", 100)
        
        # Simulate training epochs
        for epoch in range(1, total_epochs + 1):
            if job_id not in active_training_jobs:
                # Job was cancelled
                await db.training_jobs.update_one(
                    {"job_id": job_id},
                    {
                        "$set": {
                            "status": "cancelled",
                            "completed_at": datetime.utcnow()
                        },
                        "$push": {
                            "logs": f"Training cancelled at epoch {epoch}"
                        }
                    }
                )
                return
            
            # Simulate realistic training metrics
            base_loss = 2.5 * np.exp(-epoch * 0.05)
            train_loss = base_loss + np.random.normal(0, 0.1)
            val_loss = train_loss + np.random.normal(0, 0.2)
            accuracy = 1 - np.exp(-epoch * 0.1) * (0.5 + np.random.random() * 0.3)
            
            metrics = TrainingMetrics(
                epoch=epoch,
                train_loss=max(0.001, train_loss),
                val_loss=max(0.001, val_loss),
                accuracy=min(0.99, max(0.1, accuracy)),
                pr_auc=min(0.99, accuracy * 0.9 + np.random.random() * 0.1),
                lead_time_mae=max(0.5, train_loss * 2),
                confidence_calibration=min(0.99, 0.8 + np.random.random() * 0.15),
                temporal_loss=max(0.001, base_loss * 0.8 + np.random.normal(0, 0.05)),
                spatial_loss=max(0.001, base_loss * 1.2 + np.random.normal(0, 0.08)),
                fusion_loss=max(0.001, base_loss * 0.9 + np.random.normal(0, 0.06))
            )
            
            progress = (epoch / total_epochs) * 100
            
            # Update training progress
            await db.training_jobs.update_one(
                {"job_id": job_id},
                {
                    "$set": {
                        "progress": progress,
                        "current_epoch": epoch,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {
                        "metrics": metrics.dict(),
                        "logs": f"Epoch {epoch}/{total_epochs} - Loss: {train_loss:.4f}, Accuracy: {accuracy:.3f}"
                    }
                }
            )
            
            # Store in active jobs for real-time monitoring
            if job_id in active_training_jobs:
                active_training_jobs[job_id]["metrics"] = metrics.dict()
                active_training_jobs[job_id]["progress"] = progress
            
            # Simulate epoch time (faster for demo)
            await asyncio.sleep(0.5)
        
        # Training completed successfully
        performance_summary = {
            "final_accuracy": float(accuracy),
            "final_loss": float(train_loss),
            "best_pr_auc": float(max([m["pr_auc"] for m in [metrics.dict()]])),
            "training_duration_minutes": 5,
            "total_epochs": total_epochs,
            "model_components": {
                "temporal_model": config.temporal_model,
                "spatial_model": config.spatial_model,
                "fusion_model": config.fusion_model
            },
            "feature_count": {
                "temporal": sum(config.temporal_features.values()),
                "spatial": sum(config.spatial_features.values())
            }
        }
        
        await db.training_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "progress": 100.0,
                    "completed_at": datetime.utcnow(),
                    "performance_summary": performance_summary,
                    "model_paths": {
                        "temporal_model": f"/models/{job_id}/temporal_model.pth",
                        "spatial_model": f"/models/{job_id}/spatial_model.pth",
                        "fusion_model": f"/models/{job_id}/fusion_model.pth",
                        "metadata": f"/models/{job_id}/metadata.json"
                    }
                },
                "$push": {
                    "logs": "Multi-modal training completed successfully!"
                }
            }
        )
        
        # Remove from active jobs
        if job_id in active_training_jobs:
            del active_training_jobs[job_id]
            
    except Exception as e:
        logger.error(f"Training job {job_id} failed: {str(e)}")
        await db.training_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "error_message": str(e),
                    "completed_at": datetime.utcnow()
                },
                "$push": {
                    "logs": f"Training failed: {str(e)}"
                }
            }
        )
        
        if job_id in active_training_jobs:
            del active_training_jobs[job_id]


@router.post("/train", response_model=Dict[str, str])
async def start_training(
    config: TrainingConfigRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Start a new model training job"""
    try:
        job_id = str(uuid.uuid4())
        user_id = current_user.get("id", "unknown")
        
        # Create training job document
        training_job = TrainingJob(
            user_id=user_id,
            job_id=job_id,
            config=config,
            total_epochs=config.hyperparameters.get("epochs", 100),
            logs=["Training job created and queued"]
        )
        
        # Save to database
        result = await db.training_jobs.insert_one(training_job.dict())
        
        # Add to active jobs tracking
        active_training_jobs[job_id] = {
            "status": "queued",
            "progress": 0.0,
            "user_id": user_id
        }
        
        # Start training in background
        background_tasks.add_task(simulate_model_training, job_id, config, user_id, db)
        
        return {
            "job_id": job_id,
            "message": "Training job started successfully",
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Failed to start training: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")


@router.get("/status/{job_id}", response_model=TrainingStatusResponse)
async def get_training_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get training job status"""
    try:
        # Get job from database
        job = await db.training_jobs.find_one({"job_id": job_id})
        
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        # Check if user owns this job
        if job.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Calculate estimated time remaining
        estimated_time_remaining = None
        if job.get("status") == "training" and job.get("current_epoch", 0) > 0:
            remaining_epochs = job.get("total_epochs", 100) - job.get("current_epoch", 0)
            estimated_time_remaining = remaining_epochs * 30  # 30 seconds per epoch estimate
        
        # Get latest metrics
        latest_metrics = None
        if job.get("metrics"):
            latest_metrics = TrainingMetrics(**job["metrics"][-1])
        
        return TrainingStatusResponse(
            job_id=job_id,
            status=job.get("status", "unknown"),
            progress=job.get("progress", 0.0),
            current_epoch=job.get("current_epoch", 0),
            total_epochs=job.get("total_epochs", 100),
            estimated_time_remaining=estimated_time_remaining,
            latest_metrics=latest_metrics,
            logs=job.get("logs", []),
            error_message=job.get("error_message")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get training status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get training status")


@router.post("/cancel/{job_id}")
async def cancel_training(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Cancel a training job"""
    try:
        # Check if job exists and user owns it
        job = await db.training_jobs.find_one({"job_id": job_id})
        
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        if job.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if job.get("status") in ["completed", "failed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Cannot cancel completed job")
        
        # Remove from active jobs (this will cause the training loop to stop)
        if job_id in active_training_jobs:
            del active_training_jobs[job_id]
        
        # Update database
        await db.training_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "cancelled",
                    "completed_at": datetime.utcnow()
                },
                "$push": {
                    "logs": "Training cancelled by user"
                }
            }
        )
        
        return {"message": "Training job cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel training: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel training")


@router.get("/jobs", response_model=List[Dict[str, Any]])
async def get_user_training_jobs(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
    limit: int = 50,
    skip: int = 0
):
    """Get user's training jobs"""
    try:
        user_id = current_user.get("id")
        
        # Get jobs from database
        cursor = db.training_jobs.find(
            {"user_id": user_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        jobs = []
        async for job in cursor:
            job["_id"] = str(job["_id"])
            jobs.append(job)
        
        return jobs
        
    except Exception as e:
        logger.error(f"Failed to get training jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get training jobs")


@router.get("/report/{job_id}", response_model=ModelPerformanceReport)
async def get_performance_report(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Generate comprehensive performance report"""
    try:
        # Get job from database
        job = await db.training_jobs.find_one({"job_id": job_id})
        
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        if job.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        # Generate comprehensive report
        config = job.get("config", {})
        metrics = job.get("metrics", [])
        performance_summary = job.get("performance_summary", {})
        
        # Calculate feature importance (simulated)
        feature_importance = {}
        for feature, enabled in config.get("temporal_features", {}).items():
            if enabled:
                feature_importance[f"temporal_{feature}"] = np.random.random() * 0.8 + 0.1
        
        for feature, enabled in config.get("spatial_features", {}).items():
            if enabled:
                feature_importance[f"spatial_{feature}"] = np.random.random() * 0.8 + 0.1
        
        # Generate recommendations
        recommendations = []
        if performance_summary.get("final_accuracy", 0) < 0.85:
            recommendations.append("Consider increasing training epochs for better convergence")
        if config.get("hyperparameters", {}).get("learning_rate", 0.001) > 0.01:
            recommendations.append("Try reducing learning rate for more stable training")
        if config.get("advanced_options", {}).get("ensemble_methods"):
            recommendations.append("Ensemble methods are enabled - expect improved robustness")
        
        report = ModelPerformanceReport(
            job_id=job_id,
            training_summary={
                "duration_minutes": 5,
                "total_epochs": len(metrics),
                "final_metrics": metrics[-1] if metrics else {},
                "dataset_used": config.get("dataset", "unknown")
            },
            model_architecture={
                "temporal_model": config.get("temporal_model", {}),
                "spatial_model": config.get("spatial_model", {}),
                "fusion_model": config.get("fusion_model", {}),
                "advanced_options": config.get("advanced_options", {})
            },
            performance_metrics=performance_summary,
            feature_importance=feature_importance,
            validation_results={
                "cross_validation_score": np.random.random() * 0.1 + 0.85,
                "holdout_test_accuracy": np.random.random() * 0.1 + 0.8,
                "confidence_intervals": {
                    "accuracy": [0.82, 0.91],
                    "precision": [0.78, 0.89],
                    "recall": [0.81, 0.93]
                }
            },
            recommendations=recommendations
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.post("/deploy/{job_id}")
async def deploy_model(
    job_id: str,
    deployment_request: ModelDeploymentRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Deploy trained model to production"""
    try:
        # Get job from database
        job = await db.training_jobs.find_one({"job_id": job_id})
        
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        if job.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Cannot deploy incomplete training job")
        
        # Create deployment record
        deployment = {
            "deployment_id": str(uuid.uuid4()),
            "job_id": job_id,
            "name": deployment_request.deployment_name,
            "description": deployment_request.description,
            "model_paths": job.get("model_paths", {}),
            "performance_summary": job.get("performance_summary", {}),
            "deployed_by": current_user.get("id"),
            "deployed_at": datetime.utcnow(),
            "status": "active",
            "is_current": deployment_request.replace_current
        }
        
        # If replacing current, update previous deployments
        if deployment_request.replace_current:
            await db.model_deployments.update_many(
                {"is_current": True},
                {"$set": {"is_current": False}}
            )
        
        # Save deployment
        await db.model_deployments.insert_one(deployment)
        
        return {
            "message": "Model deployed successfully",
            "deployment_id": deployment["deployment_id"],
            "deployment_name": deployment_request.deployment_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deploy model: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to deploy model")


@router.get("/deployments")
async def get_deployments(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get model deployments"""
    try:
        # Get deployments from database
        cursor = db.model_deployments.find().sort("deployed_at", -1)
        
        deployments = []
        async for deployment in cursor:
            deployment["_id"] = str(deployment["_id"])
            deployments.append(deployment)
        
        return deployments
        
    except Exception as e:
        logger.error(f"Failed to get deployments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get deployments")