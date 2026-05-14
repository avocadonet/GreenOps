import uuid

from tests.e2e.conftest import auth


class TestThresholdCRUD:
    async def test_create_threshold(self, client, admin, common_sensor):
        r = await client.post(
            "/thresholds",
            json={
                "sensor_id": common_sensor["sensor_id"],
                "limit_value": 100.0,
                "threshold_type": "UPPER",
                "tariff_zone": "DAY",
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        body = r.json()
        assert body["sensor_id"] == common_sensor["sensor_id"]
        assert body["limit_value"] == 100.0
        assert body["threshold_type"] == "UPPER"
        assert body["tariff_zone"] == "DAY"
        assert "threshold_id" in body
        await client.delete(
            f"/thresholds/{body['threshold_id']}", headers=auth(admin["token"])
        )

    async def test_read_threshold(self, client, admin, common_sensor):
        r = await client.post(
            "/thresholds",
            json={
                "sensor_id": common_sensor["sensor_id"],
                "limit_value": 50.0,
                "threshold_type": "LOWER",
                "tariff_zone": "NIGHT",
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        threshold_id = r.json()["threshold_id"]

        r = await client.get(
            f"/thresholds/{threshold_id}", headers=auth(admin["token"])
        )
        assert r.status_code == 200
        assert r.json()["threshold_id"] == threshold_id

        await client.delete(f"/thresholds/{threshold_id}", headers=auth(admin["token"]))

    async def test_update_threshold(self, client, admin, common_sensor):
        r = await client.post(
            "/thresholds",
            json={
                "sensor_id": common_sensor["sensor_id"],
                "limit_value": 75.0,
                "threshold_type": "UPPER",
                "tariff_zone": "DAY",
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        threshold_id = r.json()["threshold_id"]

        r = await client.put(
            f"/thresholds/{threshold_id}",
            json={"limit_value": 200.0},
            headers=auth(admin["token"]),
        )
        assert r.status_code == 200
        assert r.json()["limit_value"] == 200.0

        await client.delete(f"/thresholds/{threshold_id}", headers=auth(admin["token"]))

    async def test_delete_threshold(self, client, admin, common_sensor):
        r = await client.post(
            "/thresholds",
            json={
                "sensor_id": common_sensor["sensor_id"],
                "limit_value": 10.0,
                "threshold_type": "LOWER",
                "tariff_zone": "DAY",
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 201
        threshold_id = r.json()["threshold_id"]

        r = await client.delete(
            f"/thresholds/{threshold_id}", headers=auth(admin["token"])
        )
        assert r.status_code == 200

        r = await client.get(
            f"/thresholds/{threshold_id}", headers=auth(admin["token"])
        )
        assert r.status_code == 404

    async def test_read_nonexistent_threshold_returns_404(self, client, admin):
        r = await client.get(
            f"/thresholds/{uuid.uuid4()}", headers=auth(admin["token"])
        )
        assert r.status_code == 404

    async def test_threshold_for_unknown_sensor_returns_404(self, client, admin):
        r = await client.post(
            "/thresholds",
            json={
                "sensor_id": str(uuid.uuid4()),
                "limit_value": 1.0,
                "threshold_type": "UPPER",
                "tariff_zone": "DAY",
            },
            headers=auth(admin["token"]),
        )
        assert r.status_code == 404
