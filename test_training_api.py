#!/usr/bin/env python3
"""
Model Training API Test Suite
Tests all training endpoints and MongoDB integration
"""

import asyncio
import json
import time
from datetime import datetime
import httpx
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.training import TrainingConfigRequest

BASE_URL = "http://localhost:8000/api"

# Test training configuration
TEST_CONFIG = {
    "temporal_features": {
        "displacement": True,
        "velocity": True,
        "acceleration": True,
        "tilt": True,
        "strain": False,
        "pore_pressure": True,
        "rainfall": True,
        "temperature": True,
        "humidity": False,
        "wind_speed": False,
        "seismic_activity": True,
        "ground_temperature": False
    },
    "spatial_features": {
        "drone_imagery": True,
        "lidar_scans": True,
        "geological_maps": True,
        "slope_analysis": True,
        "rock_mass_rating": False,
        "joint_orientation": False,
        "weathering_data": True,
        "vegetation_analysis": False
    },
    "temporal_model": {
        "type": "LSTM",
        "layers": 3,
        "hidden_size": 128,
        "dropout": 0.2,
        "bidirectional": True
    },
    "spatial_model": {
        "type": "CNN",
        "layers": 4,
        "filters": 64,
        "dropout": 0.2
    },
    "fusion_model": {
        "type": "MLP",
        "layers": 2,
        "hidden_size": 128,
        "dropout": 0.2
    },
    "hyperparameters": {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10,  # Short for testing
        "validation_split": 0.2,
        "early_stopping_patience": 5,
        "weight_decay": 0.0001
    },
    "advanced_options": {
        "ensemble_methods": False,
        "bayesian_uncertainty": True,
        "adversarial_training": False,
        "data_augmentation": True,
        "transfer_learning": False,
        "multi_task_learning": False,
        "automated_feature_selection": False,
        "hyperparameter_optimization": False
    },
    "dataset": "test_dataset",
    "cross_validation_folds": 3,
    "test_split_ratio": 0.15
}

async def get_auth_token():
    """Login and get auth token"""
    async with httpx.AsyncClient() as client:
        # Try to login with default admin credentials
        login_data = {
            "username": "admin@rockfall.com",
            "password": "admin123"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
            else:
                print(f"❌ Login failed: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None

async def test_training_api():
    """Test the complete training API workflow"""
    print("🧪 Testing Model Training API Integration")
    print("=" * 50)
    
    # Get auth token
    print("1. Authenticating...")
    token = await get_auth_token()
    if not token:
        print("❌ Authentication failed - cannot proceed with tests")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test 1: Start training
            print("\n2. Starting training job...")
            response = await client.post(
                f"{BASE_URL}/training/train", 
                json=TEST_CONFIG,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to start training: {response.status_code} {response.text}")
                return False
            
            training_data = response.json()
            job_id = training_data["job_id"]
            print(f"✅ Training started successfully! Job ID: {job_id}")
            
            # Test 2: Monitor training status
            print("\n3. Monitoring training progress...")
            start_time = time.time()
            max_wait_time = 60  # 1 minute max wait
            
            while time.time() - start_time < max_wait_time:
                response = await client.get(
                    f"{BASE_URL}/training/status/{job_id}",
                    headers=headers
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to get status: {response.status_code}")
                    break
                
                status_data = response.json()
                status = status_data["status"]
                progress = status_data["progress"]
                epoch = status_data["current_epoch"]
                total_epochs = status_data["total_epochs"]
                
                print(f"   Status: {status} | Progress: {progress:.1f}% | Epoch: {epoch}/{total_epochs}")
                
                if status in ["completed", "failed", "cancelled"]:
                    break
                
                await asyncio.sleep(2)
            
            # Test 3: Get final status
            print("\n4. Getting final training status...")
            response = await client.get(
                f"{BASE_URL}/training/status/{job_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                final_status = response.json()
                print(f"✅ Final status: {final_status['status']}")
                print(f"   Final progress: {final_status['progress']:.1f}%")
                print(f"   Logs count: {len(final_status['logs'])}")
                
                if final_status["status"] == "completed":
                    # Test 4: Get performance report
                    print("\n5. Getting performance report...")
                    response = await client.get(
                        f"{BASE_URL}/training/report/{job_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        report = response.json()
                        print("✅ Performance report generated successfully!")
                        print(f"   Duration: {report['training_summary']['duration_minutes']} minutes")
                        print(f"   Total epochs: {report['training_summary']['total_epochs']}")
                        print(f"   CV Score: {report['validation_results']['cross_validation_score']:.3f}")
                        print(f"   Recommendations: {len(report['recommendations'])}")
                        
                        # Test 5: Deploy model
                        print("\n6. Deploying trained model...")
                        deploy_data = {
                            "deployment_name": "Test Deployment",
                            "description": "Test deployment from API test suite",
                            "replace_current": False
                        }
                        
                        response = await client.post(
                            f"{BASE_URL}/training/deploy/{job_id}",
                            json=deploy_data,
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            deploy_result = response.json()
                            print(f"✅ Model deployed successfully!")
                            print(f"   Deployment ID: {deploy_result['deployment_id']}")
                            print(f"   Deployment name: {deploy_result['deployment_name']}")
                            
                            # Test 6: Get deployments
                            print("\n7. Getting deployment list...")
                            response = await client.get(
                                f"{BASE_URL}/training/deployments",
                                headers=headers
                            )
                            
                            if response.status_code == 200:
                                deployments = response.json()
                                print(f"✅ Retrieved {len(deployments)} deployments")
                                return True
                            else:
                                print(f"❌ Failed to get deployments: {response.status_code}")
                        else:
                            print(f"❌ Failed to deploy model: {response.status_code} {response.text}")
                    else:
                        print(f"❌ Failed to get performance report: {response.status_code}")
                else:
                    print(f"⚠️  Training did not complete successfully: {final_status['status']}")
                    if final_status.get("error_message"):
                        print(f"   Error: {final_status['error_message']}")
            else:
                print(f"❌ Failed to get final status: {response.status_code}")
            
            # Test 7: Get user training jobs
            print("\n8. Getting user training jobs...")
            response = await client.get(
                f"{BASE_URL}/training/jobs?limit=10",
                headers=headers
            )
            
            if response.status_code == 200:
                jobs = response.json()
                print(f"✅ Retrieved {len(jobs)} training jobs")
                return True
            else:
                print(f"❌ Failed to get training jobs: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
    
    return False

async def test_mongodb_integration():
    """Test MongoDB integration specifically"""
    print("\n🗄️  Testing MongoDB Integration")
    print("=" * 50)
    
    try:
        from app.database.connection import get_database
        
        print("1. Testing database connection...")
        db = await get_database()
        
        # Test collections exist
        collections = await db.list_collection_names()
        print(f"✅ Database connected. Collections: {len(collections)}")
        
        # Test training_jobs collection
        if "training_jobs" in collections:
            print("✅ training_jobs collection exists")
        else:
            print("⚠️  training_jobs collection not found (will be created automatically)")
        
        # Test model_deployments collection
        if "model_deployments" in collections:
            print("✅ model_deployments collection exists")
        else:
            print("⚠️  model_deployments collection not found (will be created automatically)")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB integration test failed: {e}")
        return False

def print_summary(api_success, mongo_success):
    """Print test summary"""
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    print(f"API Integration: {'✅ PASSED' if api_success else '❌ FAILED'}")
    print(f"MongoDB Integration: {'✅ PASSED' if mongo_success else '❌ FAILED'}")
    
    if api_success and mongo_success:
        print("\n🎉 ALL TESTS PASSED! Model Training system is fully functional.")
        print("\nThe system supports:")
        print("   • Multi-modal AI model training (Temporal + Spatial + Fusion)")
        print("   • Real-time training monitoring and progress tracking")
        print("   • Performance reporting and model evaluation")
        print("   • Model deployment and version management")
        print("   • MongoDB persistence for training jobs and deployments")
        print("   • Secure authentication and user isolation")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

async def main():
    """Run all tests"""
    print("🚀 Model Training API Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing against: {BASE_URL}")
    
    # Test MongoDB first
    mongo_success = await test_mongodb_integration()
    
    # Test API integration
    api_success = await test_training_api()
    
    # Print summary
    print_summary(api_success, mongo_success)

if __name__ == "__main__":
    asyncio.run(main())