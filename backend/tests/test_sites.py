"""
Tests for sites API endpoints
"""
import pytest
from conftest import TestUtils, TestDataGenerator

@pytest.mark.asyncio
class TestSitesAPI:
    """Test sites API endpoints."""
    
    async def test_get_sites_empty(self, client, auth_headers_viewer):
        """Test getting sites when none exist."""
        response = await client.get(
            "/sites/",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(data)
        
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["pages"] == 0
    
    async def test_get_sites_with_data(self, client, auth_headers_viewer, test_site):
        """Test getting sites when data exists."""
        response = await client.get(
            "/sites/",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(data)
        
        assert data["total"] == 1
        assert len(data["items"]) == 1
        
        site = data["items"][0]
        assert site["id"] == test_site["_id"]
        assert site["name"] == test_site["name"]
        assert site["status"] == test_site["status"]
    
    async def test_get_sites_pagination(self, client, auth_headers_viewer, test_db):
        """Test sites pagination."""
        # Create multiple test sites
        sites = []
        for i in range(15):
            site_data = {
                "_id": f"test_site_{i:03d}",
                "name": f"Test Site {i+1}",
                "location": {
                    "lat": 39.7392 + i * 0.001,
                    "lng": -104.9903 + i * 0.001,
                    "elevation": 1620 + i * 10
                },
                "area_hectares": 45.2 + i,
                "description": f"Test site {i+1} description",
                "status": "active"
            }
            sites.append(site_data)
        
        await test_db.sites.insert_many(sites)
        
        # Test first page
        response = await client.get(
            "/sites/?page=1&size=10",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(data)
        
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["pages"] == 2
        
        # Test second page
        response = await client.get(
            "/sites/?page=2&size=10",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        assert len(data["items"]) == 5
        assert data["page"] == 2
    
    async def test_get_site_by_id(self, client, auth_headers_viewer, test_site):
        """Test getting a specific site by ID."""
        response = await client.get(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        
        assert data["id"] == test_site["_id"]
        assert data["name"] == test_site["name"]
        assert data["location"] == test_site["location"]
        assert data["area_hectares"] == test_site["area_hectares"]
        assert data["description"] == test_site["description"]
        assert data["status"] == test_site["status"]
    
    async def test_get_nonexistent_site(self, client, auth_headers_viewer):
        """Test getting a non-existent site."""
        response = await client.get(
            "/sites/nonexistent_site",
            headers=auth_headers_viewer
        )
        
        TestUtils.assert_error_response(response, 404, "Site not found")
    
    async def test_create_site_admin(self, client, auth_headers_admin):
        """Test creating a site as admin."""
        site_data = {
            "name": "New Mining Site",
            "location": {
                "lat": 40.0,
                "lng": -105.0,
                "elevation": 1800
            },
            "area_hectares": 75.5,
            "description": "A new mining site for testing",
            "safety_protocols": [
                "Daily inspections",
                "Weather monitoring"
            ],
            "emergency_contacts": [
                {
                    "name": "Emergency Contact",
                    "role": "Site Manager",
                    "phone": "+1234567890",
                    "email": "emergency@test.com"
                }
            ]
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_admin,
            json=site_data
        )
        
        data = TestUtils.assert_valid_response(response, 201)
        
        assert data["name"] == site_data["name"]
        assert data["location"] == site_data["location"]
        assert data["area_hectares"] == site_data["area_hectares"]
        assert data["description"] == site_data["description"]
        assert data["status"] == "active"  # Default status
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    async def test_create_site_operator(self, client, auth_headers_operator):
        """Test creating a site as operator."""
        site_data = {
            "name": "Operator Site",
            "location": {"lat": 41.0, "lng": -106.0, "elevation": 1900},
            "area_hectares": 50.0,
            "description": "Site created by operator"
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_operator,
            json=site_data
        )
        
        data = TestUtils.assert_valid_response(response, 201)
        assert data["name"] == site_data["name"]
    
    async def test_create_site_viewer_forbidden(self, client, auth_headers_viewer):
        """Test that viewer cannot create sites."""
        site_data = {
            "name": "Forbidden Site",
            "location": {"lat": 42.0, "lng": -107.0, "elevation": 2000},
            "area_hectares": 30.0,
            "description": "This should fail"
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_viewer,
            json=site_data
        )
        
        TestUtils.assert_error_response(response, 403, "Not enough permissions")
    
    async def test_create_site_invalid_data(self, client, auth_headers_admin):
        """Test creating site with invalid data."""
        # Missing required fields
        site_data = {
            "name": "Incomplete Site"
            # Missing location, area_hectares, description
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_admin,
            json=site_data
        )
        
        TestUtils.assert_error_response(response, 422)  # Validation error
    
    async def test_update_site(self, client, auth_headers_admin, test_site):
        """Test updating a site."""
        update_data = {
            "name": "Updated Site Name",
            "description": "Updated description",
            "area_hectares": 60.0,
            "status": "maintenance"
        }
        
        response = await client.put(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_admin,
            json=update_data
        )
        
        data = TestUtils.assert_valid_response(response)
        
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["area_hectares"] == update_data["area_hectares"]
        assert data["status"] == update_data["status"]
        assert data["location"] == test_site["location"]  # Should remain unchanged
    
    async def test_update_site_partial(self, client, auth_headers_admin, test_site):
        """Test partial update of a site."""
        update_data = {
            "description": "Only updating description"
        }
        
        response = await client.put(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_admin,
            json=update_data
        )
        
        data = TestUtils.assert_valid_response(response)
        
        assert data["description"] == update_data["description"]
        assert data["name"] == test_site["name"]  # Should remain unchanged
        assert data["location"] == test_site["location"]  # Should remain unchanged
    
    async def test_update_nonexistent_site(self, client, auth_headers_admin):
        """Test updating a non-existent site."""
        update_data = {
            "name": "Updated Name"
        }
        
        response = await client.put(
            "/sites/nonexistent_site",
            headers=auth_headers_admin,
            json=update_data
        )
        
        TestUtils.assert_error_response(response, 404, "Site not found")
    
    async def test_update_site_viewer_forbidden(self, client, auth_headers_viewer, test_site):
        """Test that viewer cannot update sites."""
        update_data = {
            "name": "Forbidden Update"
        }
        
        response = await client.put(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_viewer,
            json=update_data
        )
        
        TestUtils.assert_error_response(response, 403, "Not enough permissions")
    
    async def test_delete_site(self, client, auth_headers_admin, test_site):
        """Test deleting a site."""
        response = await client.delete(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 204
        
        # Verify site is deleted
        response = await client.get(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_admin
        )
        
        TestUtils.assert_error_response(response, 404, "Site not found")
    
    async def test_delete_nonexistent_site(self, client, auth_headers_admin):
        """Test deleting a non-existent site."""
        response = await client.delete(
            "/sites/nonexistent_site",
            headers=auth_headers_admin
        )
        
        TestUtils.assert_error_response(response, 404, "Site not found")
    
    async def test_delete_site_operator_forbidden(self, client, auth_headers_operator, test_site):
        """Test that operator cannot delete sites."""
        response = await client.delete(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_operator
        )
        
        TestUtils.assert_error_response(response, 403, "Not enough permissions")
    
    async def test_delete_site_viewer_forbidden(self, client, auth_headers_viewer, test_site):
        """Test that viewer cannot delete sites."""
        response = await client.delete(
            f"/sites/{test_site['_id']}",
            headers=auth_headers_viewer
        )
        
        TestUtils.assert_error_response(response, 403, "Not enough permissions")

@pytest.mark.asyncio
class TestSitesFiltering:
    """Test sites filtering and search functionality."""
    
    async def test_filter_sites_by_status(self, client, auth_headers_viewer, test_db):
        """Test filtering sites by status."""
        # Create sites with different statuses
        sites = [
            {
                "_id": "active_site_1",
                "name": "Active Site 1",
                "location": {"lat": 39.7, "lng": -104.9, "elevation": 1600},
                "area_hectares": 45.0,
                "description": "Active site",
                "status": "active"
            },
            {
                "_id": "active_site_2", 
                "name": "Active Site 2",
                "location": {"lat": 39.8, "lng": -104.8, "elevation": 1700},
                "area_hectares": 55.0,
                "description": "Another active site",
                "status": "active"
            },
            {
                "_id": "maintenance_site",
                "name": "Maintenance Site",
                "location": {"lat": 39.9, "lng": -104.7, "elevation": 1800},
                "area_hectares": 35.0,
                "description": "Site under maintenance",
                "status": "maintenance"
            }
        ]
        
        await test_db.sites.insert_many(sites)
        
        # Filter for active sites
        response = await client.get(
            "/sites/?status=active",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        assert data["total"] == 2
        
        for site in data["items"]:
            assert site["status"] == "active"
        
        # Filter for maintenance sites
        response = await client.get(
            "/sites/?status=maintenance",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        assert data["total"] == 1
        assert data["items"][0]["status"] == "maintenance"
    
    async def test_search_sites_by_name(self, client, auth_headers_viewer, test_db):
        """Test searching sites by name."""
        sites = [
            {
                "_id": "quarry_site",
                "name": "Rocky Mountain Quarry",
                "location": {"lat": 39.7, "lng": -104.9, "elevation": 1600},
                "area_hectares": 45.0,
                "description": "Limestone quarry",
                "status": "active"
            },
            {
                "_id": "mine_site",
                "name": "Sierra Nevada Mine",
                "location": {"lat": 39.8, "lng": -104.8, "elevation": 1700},
                "area_hectares": 75.0,
                "description": "Copper mine",
                "status": "active"
            }
        ]
        
        await test_db.sites.insert_many(sites)
        
        # Search for "quarry"
        response = await client.get(
            "/sites/?search=quarry",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        assert data["total"] == 1
        assert "quarry" in data["items"][0]["name"].lower()
        
        # Search for "mountain"
        response = await client.get(
            "/sites/?search=mountain",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        assert data["total"] == 1
        assert "mountain" in data["items"][0]["name"].lower()
    
    async def test_sort_sites(self, client, auth_headers_viewer, test_db):
        """Test sorting sites."""
        sites = [
            {
                "_id": "site_c",
                "name": "C Site",
                "location": {"lat": 39.7, "lng": -104.9, "elevation": 1600},
                "area_hectares": 30.0,
                "description": "Site C",
                "status": "active"
            },
            {
                "_id": "site_a",
                "name": "A Site",
                "location": {"lat": 39.8, "lng": -104.8, "elevation": 1700},
                "area_hectares": 50.0,
                "description": "Site A",
                "status": "active"
            },
            {
                "_id": "site_b",
                "name": "B Site",
                "location": {"lat": 39.9, "lng": -104.7, "elevation": 1800},
                "area_hectares": 40.0,
                "description": "Site B",
                "status": "active"
            }
        ]
        
        await test_db.sites.insert_many(sites)
        
        # Sort by name ascending
        response = await client.get(
            "/sites/?sort_by=name&sort_order=asc",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        names = [site["name"] for site in data["items"]]
        assert names == ["A Site", "B Site", "C Site"]
        
        # Sort by area descending
        response = await client.get(
            "/sites/?sort_by=area_hectares&sort_order=desc",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        areas = [site["area_hectares"] for site in data["items"]]
        assert areas == [50.0, 40.0, 30.0]