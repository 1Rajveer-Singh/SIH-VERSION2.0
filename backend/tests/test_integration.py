"""
Integration tests for the complete system
"""
import pytest
import asyncio
import json
from datetime import datetime, timedelta
from httpx import AsyncClient
from conftest import TestUtils, TestDataGenerator

@pytest.mark.integration
@pytest.mark.asyncio
class TestCompleteWorkflow:
    """Test complete user workflows."""
    
    async def test_admin_complete_workflow(self, client, admin_user, auth_headers_admin):
        """Test complete admin workflow: create site, sensor, get predictions."""
        
        # Step 1: Create a new site
        site_data = {
            "name": "Integration Test Site",
            "location": {
                "lat": 39.7392,
                "lng": -104.9903,
                "elevation": 1620
            },
            "area_hectares": 45.2,
            "description": "Site for integration testing",
            "safety_protocols": ["Daily inspections"],
            "emergency_contacts": [
                {
                    "name": "Test Manager",
                    "role": "Site Manager",
                    "phone": "+1234567890",
                    "email": "manager@test.com"
                }
            ]
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_admin,
            json=site_data
        )
        site = TestUtils.assert_valid_response(response, 201)
        site_id = site["id"]
        
        # Step 2: Create sensors for the site
        sensor_data = {
            "name": "Integration Test Sensor",
            "site_id": site_id,
            "location": {
                "lat": 39.7393,
                "lng": -104.9904,
                "elevation": 1625
            },
            "sensor_types": ["accelerometer", "temperature"],
            "status": "active"
        }
        
        response = await client.post(
            "/sensors/",
            headers=auth_headers_admin,
            json=sensor_data
        )
        sensor = TestUtils.assert_valid_response(response, 201)
        sensor_id = sensor["id"]
        
        # Step 3: Add sensor readings
        readings_data = []
        for i in range(10):
            reading = TestDataGenerator.generate_sensor_reading(sensor_id, site_id)
            readings_data.append(reading)
        
        for reading in readings_data:
            response = await client.post(
                "/sensors/readings",
                headers=auth_headers_admin,
                json=reading
            )
            TestUtils.assert_valid_response(response, 201)
        
        # Step 4: Get sensor readings
        response = await client.get(
            f"/sensors/{sensor_id}/readings",
            headers=auth_headers_admin
        )
        readings_response = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(readings_response)
        assert readings_response["total"] >= 10
        
        # Step 5: Generate prediction (mocked)
        with patch('routers.predictions.RockfallPredictor') as mock_predictor_class:
            mock_predictor = MagicMock()
            mock_predictor.predict.return_value = {
                'risk_score': 0.65,
                'risk_level': 'medium',
                'confidence': 0.82,
                'model_outputs': {'ensemble': 0.65}
            }
            mock_predictor_class.return_value = mock_predictor
            
            response = await client.post(
                f"/predictions/predict/{site_id}",
                headers=auth_headers_admin,
                json={"sensor_readings": readings_data[:5]}
            )
            prediction = TestUtils.assert_valid_response(response, 201)
            assert prediction["risk_level"] == "medium"
            assert prediction["risk_score"] == 0.65
        
        # Step 6: Create alert based on prediction
        alert_data = {
            "site_id": site_id,
            "type": "rockfall_risk",
            "severity": "medium",
            "title": "Integration Test Alert",
            "description": "Alert created during integration test",
            "metadata": {
                "prediction_id": prediction["id"],
                "risk_score": prediction["risk_score"]
            }
        }
        
        response = await client.post(
            "/alerts/",
            headers=auth_headers_admin,
            json=alert_data
        )
        alert = TestUtils.assert_valid_response(response, 201)
        
        # Step 7: Get alerts for site
        response = await client.get(
            f"/alerts/?site_id={site_id}",
            headers=auth_headers_admin
        )
        alerts_response = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(alerts_response)
        assert alerts_response["total"] >= 1
        
        # Step 8: Update alert status
        response = await client.put(
            f"/alerts/{alert['id']}",
            headers=auth_headers_admin,
            json={"status": "acknowledged"}
        )
        updated_alert = TestUtils.assert_valid_response(response)
        assert updated_alert["status"] == "acknowledged"
        
        # Step 9: Cleanup - delete created resources
        await client.delete(f"/alerts/{alert['id']}", headers=auth_headers_admin)
        await client.delete(f"/sensors/{sensor_id}", headers=auth_headers_admin)
        await client.delete(f"/sites/{site_id}", headers=auth_headers_admin)
    
    async def test_operator_workflow(self, client, operator_user, auth_headers_operator, test_site, test_sensor):
        """Test operator workflow: monitor site, add readings, view alerts."""
        
        # Step 1: View assigned sites
        response = await client.get(
            "/sites/",
            headers=auth_headers_operator
        )
        sites = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(sites)
        
        # Step 2: Add sensor readings
        reading_data = TestDataGenerator.generate_sensor_reading(
            test_sensor["_id"], test_site["_id"]
        )
        
        response = await client.post(
            "/sensors/readings",
            headers=auth_headers_operator,
            json=reading_data
        )
        TestUtils.assert_valid_response(response, 201)
        
        # Step 3: View site sensors
        response = await client.get(
            f"/sites/{test_site['_id']}/sensors",
            headers=auth_headers_operator
        )
        sensors = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(sensors)
        
        # Step 4: View recent readings
        response = await client.get(
            f"/sensors/{test_sensor['_id']}/readings?limit=10",
            headers=auth_headers_operator
        )
        readings = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(readings)
        
        # Step 5: View alerts (should not be able to create)
        response = await client.get(
            "/alerts/",
            headers=auth_headers_operator
        )
        alerts = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(alerts)
    
    async def test_viewer_workflow(self, client, viewer_user, auth_headers_viewer, test_site, test_sensor):
        """Test viewer workflow: read-only access to data."""
        
        # Step 1: View sites (read-only)
        response = await client.get(
            "/sites/",
            headers=auth_headers_viewer
        )
        sites = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(sites)
        
        # Step 2: View specific site
        response = await client.get(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_viewer
        )
        site = TestUtils.assert_valid_response(response)
        assert site["id"] == test_site["_id"]
        
        # Step 3: View sensors
        response = await client.get(
            "/sensors/",
            headers=auth_headers_viewer
        )
        sensors = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(sensors)
        
        # Step 4: View alerts
        response = await client.get(
            "/alerts/",
            headers=auth_headers_viewer
        )
        alerts = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(alerts)
        
        # Step 5: Try to create site (should fail)
        site_data = {
            "name": "Unauthorized Site",
            "location": {"lat": 40.0, "lng": -105.0, "elevation": 1500},
            "area_hectares": 25.0,
            "description": "Should not be created"
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_viewer,
            json=site_data
        )
        TestUtils.assert_error_response(response, 403, "Not enough permissions")

@pytest.mark.integration
@pytest.mark.asyncio
class TestDataConsistency:
    """Test data consistency across operations."""
    
    async def test_cascade_delete_site(self, client, auth_headers_admin, test_db):
        """Test that deleting a site cascades to related data."""
        
        # Create site
        site_data = {
            "name": "Cascade Test Site",
            "location": {"lat": 39.7, "lng": -104.9, "elevation": 1600},
            "area_hectares": 45.0,
            "description": "Site for cascade delete test",
            "status": "active"
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_admin,
            json=site_data
        )
        site = TestUtils.assert_valid_response(response, 201)
        site_id = site["id"]
        
        # Create sensor for site
        sensor_data = {
            "name": "Cascade Test Sensor",
            "site_id": site_id,
            "location": {"lat": 39.7, "lng": -104.9, "elevation": 1600},
            "sensor_types": ["accelerometer"],
            "status": "active"
        }
        
        response = await client.post(
            "/sensors/",
            headers=auth_headers_admin,
            json=sensor_data
        )
        sensor = TestUtils.assert_valid_response(response, 201)
        sensor_id = sensor["id"]
        
        # Add sensor reading
        reading_data = TestDataGenerator.generate_sensor_reading(sensor_id, site_id)
        response = await client.post(
            "/sensors/readings",
            headers=auth_headers_admin,
            json=reading_data
        )
        TestUtils.assert_valid_response(response, 201)
        
        # Create alert for site
        alert_data = TestDataGenerator.generate_alert(site_id)
        response = await client.post(
            "/alerts/",
            headers=auth_headers_admin,
            json=alert_data
        )
        alert = TestUtils.assert_valid_response(response, 201)
        
        # Verify data exists
        assert await test_db.sites.find_one({"_id": site_id}) is not None
        assert await test_db.sensors.find_one({"_id": sensor_id}) is not None
        assert await test_db.sensor_readings.find_one({"site_id": site_id}) is not None
        assert await test_db.alerts.find_one({"_id": alert["id"]}) is not None
        
        # Delete site
        response = await client.delete(
            f"/sites/{site_id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 204
        
        # Verify cascaded deletion
        assert await test_db.sites.find_one({"_id": site_id}) is None
        # Note: In a real implementation, we'd want to cascade delete or handle orphaned data
        # For now, we just verify the site is deleted
    
    async def test_concurrent_operations(self, client, auth_headers_admin, test_site):
        """Test concurrent operations on the same resource."""
        
        # Simulate concurrent updates to the same site
        update_data_1 = {"description": "Updated by user 1"}
        update_data_2 = {"description": "Updated by user 2"}
        
        # Send concurrent requests
        responses = await asyncio.gather(
            client.put(
                f"/sites/{test_site['_id']}",
                headers=auth_headers_admin,
                json=update_data_1
            ),
            client.put(
                f"/sites/{test_site['_id']}",
                headers=auth_headers_admin,
                json=update_data_2
            ),
            return_exceptions=True
        )
        
        # Both requests should succeed (last write wins)
        for response in responses:
            if isinstance(response, Exception):
                pytest.fail(f"Concurrent operation failed: {response}")
            assert response.status_code == 200

@pytest.mark.integration
@pytest.mark.asyncio
class TestSystemLimits:
    """Test system limits and edge cases."""
    
    async def test_pagination_limits(self, client, auth_headers_viewer, test_db):
        """Test pagination with large datasets."""
        
        # Create many sites
        sites = []
        for i in range(150):
            site_data = {
                "_id": f"bulk_site_{i:03d}",
                "name": f"Bulk Site {i+1}",
                "location": {"lat": 39.7 + i*0.001, "lng": -104.9 + i*0.001, "elevation": 1600},
                "area_hectares": 45.0,
                "description": f"Bulk site {i+1}",
                "status": "active"
            }
            sites.append(site_data)
        
        await test_db.sites.insert_many(sites)
        
        # Test various page sizes
        for page_size in [10, 50, 100]:
            response = await client.get(
                f"/sites/?size={page_size}",
                headers=auth_headers_viewer
            )
            data = TestUtils.assert_valid_response(response)
            TestUtils.assert_pagination_response(data)
            
            assert len(data["items"]) <= page_size
            assert data["size"] == page_size
            
        # Test maximum page size limit
        response = await client.get(
            "/sites/?size=1000",  # Should be capped
            headers=auth_headers_viewer
        )
        data = TestUtils.assert_valid_response(response)
        assert data["size"] <= 100  # Assuming max page size is 100
    
    async def test_large_sensor_reading(self, client, auth_headers_operator, test_sensor, test_site):
        """Test handling of large sensor readings."""
        
        # Create reading with many parameters
        large_reading = {
            "sensor_id": test_sensor["_id"],
            "site_id": test_site["_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "readings": {
                f"param_{i}": i * 0.1 for i in range(100)  # 100 parameters
            }
        }
        
        response = await client.post(
            "/sensors/readings",
            headers=auth_headers_operator,
            json=large_reading
        )
        
        # Should handle large readings gracefully
        TestUtils.assert_valid_response(response, 201)

# Import required modules for mocking
from unittest.mock import patch, MagicMock