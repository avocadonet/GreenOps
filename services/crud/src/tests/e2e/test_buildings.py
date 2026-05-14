import uuid

from tests.e2e.conftest import auth


class TestBuildingCRUD:
    async def test_create_building(self, client, admin):
        r = await client.post(
            "/buildings",
            json={
                "address": "Create St 1",
                "building_type": "RESIDENTIAL",
                "total_area": 150.0,
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        body = r.json()
        assert body["address"] == "Create St 1"
        assert body["building_type"] == "RESIDENTIAL"
        assert body["total_area"] == 150.0
        assert "building_id" in body

        # Cleanup
        await client.delete(
            f"/buildings/{body['building_id']}", headers=auth(admin["token"])
        )

    async def test_read_building(self, client, admin, building):
        r = await client.get(
            f"/buildings/{building['building_id']}", headers=auth(admin["token"])
        )
        assert r.status_code == 200
        assert r.json()["building_id"] == building["building_id"]

    async def test_update_building(self, client, admin, building):
        r = await client.put(
            f"/buildings/{building['building_id']}",
            json={"address": "Updated Ave 99", "total_area": 999.0},
            headers=auth(admin["token"]),
        )
        assert r.status_code == 200
        body = r.json()
        assert body["address"] == "Updated Ave 99"
        assert body["total_area"] == 999.0

    async def test_delete_building(self, client, admin):
        r = await client.post(
            "/buildings",
            json={
                "address": "Delete Me St",
                "building_type": "INDUSTRIAL",
                "total_area": 50.0,
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        building_id = r.json()["building_id"]

        r = await client.delete(
            f"/buildings/{building_id}", headers=auth(admin["token"])
        )
        assert r.status_code == 200

        r = await client.get(f"/buildings/{building_id}", headers=auth(admin["token"]))
        assert r.status_code == 404

    async def test_read_nonexistent_building_returns_404(self, client, admin):
        fake_id = uuid.uuid4()
        r = await client.get(f"/buildings/{fake_id}", headers=auth(admin["token"]))
        assert r.status_code == 404

    async def test_update_nonexistent_building_returns_404(self, client, admin):
        fake_id = uuid.uuid4()
        r = await client.put(
            f"/buildings/{fake_id}",
            json={"address": "Ghost St", "total_area": 1.0},
            headers=auth(admin["token"]),
        )
        assert r.status_code == 404


class TestBuildingPermissions:
    async def test_no_auth_header_returns_422(self, client):
        r = await client.post(
            "/buildings",
            json={
                "address": "Unauth St",
                "building_type": "RESIDENTIAL",
                "total_area": 10.0,
            },
        )
        assert r.status_code == 422

    async def test_public_user_cannot_create(self, client, public_user):
        r = await client.post(
            "/buildings",
            json={
                "address": "Forbidden",
                "building_type": "RESIDENTIAL",
                "total_area": 10.0,
            },
            headers=auth(public_user["token"]),
        )
        assert r.status_code == 403

    async def test_public_user_cannot_read(self, client, public_user, building):
        r = await client.get(
            f"/buildings/{building['building_id']}", headers=auth(public_user["token"])
        )
        assert r.status_code == 403
