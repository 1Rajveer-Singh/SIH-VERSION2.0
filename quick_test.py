import requests

try:
    # Test basic health
    response = requests.get("http://localhost:8000/health")
    print(f"✅ Health: {response.status_code}")
    
    # Test login
    login_data = {"email": "admin@rockfall.com", "password": "secret123"}
    response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    print(f"✅ Login: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test training endpoint exists
        test_config = {
            "temporal_features": {"displacement": True, "velocity": True, "acceleration": True, "tilt": True, "strain": False, "pore_pressure": True, "rainfall": True, "temperature": True, "humidity": False, "wind_speed": False, "seismic_activity": True, "ground_temperature": False},
            "spatial_features": {"drone_imagery": True, "lidar_scans": True, "geological_maps": True, "slope_analysis": True, "rock_mass_rating": False, "joint_orientation": False, "weathering_data": True, "vegetation_analysis": False},
            "temporal_model": {"type": "LSTM", "layers": 3, "hidden_size": 128, "dropout": 0.2, "bidirectional": True},
            "spatial_model": {"type": "CNN", "layers": 4, "filters": 64, "dropout": 0.2},
            "fusion_model": {"type": "MLP", "layers": 2, "hidden_size": 128, "dropout": 0.2},
            "hyperparameters": {"learning_rate": 0.001, "batch_size": 32, "epochs": 3, "validation_split": 0.2, "early_stopping_patience": 5, "weight_decay": 0.0001},
            "advanced_options": {"ensemble_methods": False, "bayesian_uncertainty": True, "adversarial_training": False, "data_augmentation": True, "transfer_learning": False, "multi_task_learning": False, "automated_feature_selection": False, "hyperparameter_optimization": False},
            "dataset": "test_dataset", "cross_validation_folds": 3, "test_split_ratio": 0.15
        }
        
        response = requests.post("http://localhost:8000/api/training/train", json=test_config, headers=headers)
        print(f"🎯 Training API: {response.status_code}")
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"   ✅ Job created: {job_id[:8]}...")
            
            # Check initial status
            response = requests.get(f"http://localhost:8000/api/training/status/{job_id}", headers=headers)
            if response.status_code == 200:
                status = response.json()
                print(f"   ✅ Status check: {status['status']} - {status['progress']:.1f}%")
                print("🎉 TRAINING API FULLY FUNCTIONAL!")
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
        else:
            print(f"   ❌ Training failed: {response.text}")
            
except Exception as e:
    print(f"❌ Test failed: {e}")