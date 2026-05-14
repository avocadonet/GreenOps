import uuid

from tests.e2e.conftest import auth


class TestSensorCRUD:
    async def test_create_common_sensor(self, client, admin, building):
        r = await client.post(
            "/sensors",
            json={
                "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
                "model": "Common Model X",
                "calibration_date": "2024-06-01",
                "sensor_type": "COMMON",
                "building_id": building["building_id"],
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        body = r.json()
        assert body["sensor_type"] == "COMMON"
        assert body["building_id"] == building["building_id"]
        assert body["unit_id"] is None
        await client.delete(
            f"/sensors/{body['sensor_id']}", headers=auth(admin["token"])
        )

    async def test_create_individual_sensor(self, client, admin, unit):
        r = await client.post(
            "/sensors",
            json={
                "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
                "model": "Individual Model Y",
                "calibration_date": "2024-06-01",
                "sensor_type": "INDIVIDUAL",
                "unit_id": unit["unit_id"],
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        body = r.json()
        assert body["sensor_type"] == "INDIVIDUAL"
        assert body["unit_id"] == unit["unit_id"]
        assert body["building_id"] is None
        await client.delete(
            f"/sensors/{body['sensor_id']}", headers=auth(admin["token"])
        )

    async def test_read_sensor(self, client, admin, common_sensor):
        r = await client.get(
            f"/sensors/{common_sensor['sensor_id']}", headers=auth(admin["token"])
        )
        assert r.status_code == 200
        assert r.json()["sensor_id"] == common_sensor["sensor_id"]

    async def test_update_sensor(self, client, admin, common_sensor):
        r = await client.put(
            f"/sensors/{common_sensor['sensor_id']}",
            json={
                "serial_number": "SN-UPDATED",
                "model": "Updated Model",
                "calibration_date": "2025-01-01",
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 200
        body = r.json()
        assert body["serial_number"] == "SN-UPDATED"
        assert body["model"] == "Updated Model"

    async def test_delete_sensor(self, client, admin, building):
        r = await client.post(
            "/sensors",
            json={
                "serial_number": f"SN-DEL-{uuid.uuid4().hex[:6]}",
                "model": "Delete Me",
                "calibration_date": "2024-01-01",
                "sensor_type": "COMMON",
                "building_id": building["building_id"],
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        sensor_id = r.json()["sensor_id"]

        r = await client.delete(f"/sensors/{sensor_id}", headers=auth(admin["token"]))
        assert r.status_code == 200

        r = await client.get(f"/sensors/{sensor_id}", headers=auth(admin["token"]))
        assert r.status_code == 404

    async def test_read_nonexistent_sensor_returns_404(self, client, admin):
        r = await client.get(f"/sensors/{uuid.uuid4()}", headers=auth(admin["token"]))
        assert r.status_code == 404


class TestSensorAttachmentValidation:
    async def test_no_attachment_returns_422(self, client, admin):
        r = await client.post(
            "/sensors",
            json={
                "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
                "model": "No Attach",
                "calibration_date": "2024-01-01",
                "sensor_type": "COMMON",
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 422

    async def test_dual_attachment_returns_422(self, client, admin, building, unit):
        r = await client.post(
            "/sensors",
            json={
                "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
                "model": "Dual Attach",
                "calibration_date": "2024-01-01",
                "sensor_type": "COMMON",
                "building_id": building["building_id"],
                "unit_id": unit["unit_id"],
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 422

    async def test_common_sensor_requires_building_not_unit(self, client, admin, unit):
        r = await client.post(
            "/sensors",
            json={
                "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
                "model": "Wrong Attach",
                "calibration_date": "2024-01-01",
                "sensor_type": "COMMON",
                "unit_id": unit["unit_id"],
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 422

    async def test_individual_sensor_requires_unit_not_building(
        self, client, admin, building
    ):
        r = await client.post(
            "/sensors",
            json={
                "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
                "model": "Wrong Attach",
                "calibration_date": "2024-01-01",
                "sensor_type": "INDIVIDUAL",
                "building_id": building["building_id"],
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 422
