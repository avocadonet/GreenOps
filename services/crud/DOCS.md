# GreenOps CRUD Service

REST API service that manages the core domain entities of the GreenOps platform — buildings, units, sensors, thresholds, and energy balance analytics. Provides JWT authentication, role-based access control, and exposes Prometheus metrics.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Running the Service](#running-the-service)
- [Authentication](#authentication)
- [Roles & Permissions](#roles--permissions)
- [API Reference](#api-reference)
  - [Auth](#auth)
  - [Buildings](#buildings)
  - [Units](#units)
  - [Sensors](#sensors)
  - [Thresholds](#thresholds)
  - [Energy Balances](#energy-balances)
- [Domain Model](#domain-model)
- [Scheduled Jobs](#scheduled-jobs)
- [Error Responses](#error-responses)

---

## Overview

| Property | Value |
|---|---|
| Python | 3.12+ |
| Framework | FastAPI 0.122+ |
| Database | PostgreSQL (via asyncpg + SQLAlchemy 2.0) |
| Auth | JWT (HS256), bcrypt password hashing |
| DI | Dishka |
| Migrations | Alembic (shared package) |
| Metrics | Prometheus (`/metrics`) |

---

## Architecture

```
src/
├── application/        # Use cases, services, permission logic
│   ├── auth/           # JWT / bcrypt gateways, auth use cases
│   ├── building/
│   ├── unit/
│   ├── sensor/
│   ├── threshold/
│   ├── energy_balance/
│   └── average_load/
├── domain/             # Abstract repositories, domain exceptions
├── infrastructure/
│   ├── api/            # FastAPI routers, schemas, mappers, dependencies
│   ├── auth/           # Concrete JWT and bcrypt implementations
│   ├── configs/        # Config dataclass, env loading
│   ├── db/             # SQLAlchemy repository implementations
│   ├── providers/      # Dishka DI providers
│   └── scheduler/      # APScheduler jobs
```

The service follows clean architecture: the `domain` layer has no dependencies, `application` depends only on `domain`, and `infrastructure` implements everything concrete.

---

## Configuration

All configuration is read from environment variables.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL DSN, e.g. `postgresql+asyncpg://user:pass@host/db` |
| `JWT_SECRET_KEY` | Yes | Secret used to sign and verify JWT tokens |

In the Docker Compose setup these are provided under the `crud` service environment block.

---

## Running the Service

**With Docker Compose (recommended):**
```bash
docker compose up crud
```

**Locally:**
```bash
cd services/crud
poetry install
DATABASE_URL=postgresql+asyncpg://... JWT_SECRET_KEY=... \
  poetry run uvicorn infrastructure.api.app:create_app \
    --factory --host 0.0.0.0 --port 8000 --reload
```

**Run migrations separately:**
```bash
docker compose run migrations
```

The service listens on port **8000**. Interactive API docs are available at `/docs`.

---

## Authentication

The service uses **Bearer JWT tokens**. Every protected endpoint requires the header:

```
Authorization: Bearer <access_token>
```

### Login

`POST /auth/login` — exchange email + password for a token pair.

The returned `access_token` expires in **1 hour**. The `refresh_token` is valid for **30 days** (token refresh endpoint is not yet exposed; re-login to get a new pair).

### Token Validation Flow

1. The `Authorization` header is parsed by `get_current_user` (see `infrastructure/api/dependencies.py`).
2. `JwtTokensGateway` verifies the signature and expiry.
3. `AuthorizeUseCase` looks up the user by the token subject (email).
4. The resolved `User` entity (including its `role`) is passed to `require_permission`.

---

## Roles & Permissions

Every user has exactly one role stored in `users.role`. The role determines which endpoints they can call.

### Roles

| Role | Description |
|---|---|
| `SUPER_USER` | Platform superuser — unrestricted |
| `SUPER_OWNER` | Platform owner — unrestricted |
| `SUPER_ADMIN` | Platform admin — unrestricted |
| `SUPER_REDACTOR` | Platform redactor — unrestricted |
| `ADMIN` | Organisation admin — full CRUD on all resources |
| `REDACTOR` | Energy analyst / dispatcher — reads infra, manages thresholds |
| `OWNER` | Organisation director — read-only on all resources |
| `PUBLIC` | Resident — no access to infrastructure endpoints |

New users receive `PUBLIC` by default.

### Permission Matrix

| Permission | SUPER_* | ADMIN | REDACTOR | OWNER | PUBLIC |
|---|:---:|:---:|:---:|:---:|:---:|
| CAN_READ_BUILDING | ✓ | ✓ | ✓ | ✓ | — |
| CAN_CREATE_BUILDING | ✓ | ✓ | — | — | — |
| CAN_UPDATE_BUILDING | ✓ | ✓ | — | — | — |
| CAN_DELETE_BUILDING | ✓ | ✓ | — | — | — |
| CAN_READ_UNIT | ✓ | ✓ | ✓ | ✓ | — |
| CAN_CREATE_UNIT | ✓ | ✓ | — | — | — |
| CAN_UPDATE_UNIT | ✓ | ✓ | — | — | — |
| CAN_DELETE_UNIT | ✓ | ✓ | — | — | — |
| CAN_READ_SENSOR | ✓ | ✓ | ✓ | ✓ | — |
| CAN_CREATE_SENSOR | ✓ | ✓ | — | — | — |
| CAN_UPDATE_SENSOR | ✓ | ✓ | — | — | — |
| CAN_DELETE_SENSOR | ✓ | ✓ | — | — | — |
| CAN_READ_THRESHOLD | ✓ | ✓ | ✓ | ✓ | — |
| CAN_CREATE_THRESHOLD | ✓ | ✓ | ✓ | — | — |
| CAN_UPDATE_THRESHOLD | ✓ | ✓ | ✓ | — | — |
| CAN_DELETE_THRESHOLD | ✓ | ✓ | ✓ | — | — |
| CAN_READ_ENERGY_BALANCE | ✓ | ✓ | ✓ | ✓ | — |

---

## API Reference

All responses use `application/json`. UUIDs are in standard hyphenated format. Datetimes are ISO 8601 with timezone.

### Auth

#### `POST /auth/register`

Register a new user account. The account is created inactive (`is_active=false`).

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "s3cr3t",
  "fullname": "Jane Doe"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string (email) | Yes | Must be unique |
| `password` | string | Yes | Plain text; stored as bcrypt hash |
| `fullname` | string | No | Defaults to `""` |

**Response `201`:**
```json
{
  "message": "User registered successfully",
  "user_id": 42,
  "email": "user@example.com"
}
```

**Error `409`** — email already taken.

---

#### `POST /auth/login`

Exchange credentials for a JWT token pair.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "s3cr3t"
}
```

**Response `200`:**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "user_id": 42,
  "email": "user@example.com"
}
```

**Error `401`** — wrong credentials or inactive account.

---

### Buildings

> Requires `Authorization: Bearer <token>` on all endpoints.

A building represents a physical property managed by the organisation.

#### `POST /buildings` — `CAN_CREATE_BUILDING`

**Request body:**
```json
{
  "address": "ул. Ленина 1",
  "building_type": "RESIDENTIAL",
  "total_area": 3200.5
}
```

| Field | Type | Notes |
|---|---|---|
| `address` | string | Street address |
| `building_type` | enum | See `BuildingType` |
| `total_area` | float | Total area in m² |

**Response `201`:** `BuildingResponse`

---

#### `GET /buildings/{building_id}` — `CAN_READ_BUILDING`

**Path param:** `building_id` — UUID

**Response `200`:**
```json
{
  "building_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "address": "ул. Ленина 1",
  "building_type": "RESIDENTIAL",
  "total_area": 3200.5
}
```

**Error `404`** — building not found.

---

#### `PUT /buildings/{building_id}` — `CAN_UPDATE_BUILDING`

**Request body:**
```json
{
  "address": "ул. Ленина 2",
  "total_area": 3300.0
}
```

**Response `200`:** updated `BuildingResponse`.

---

#### `DELETE /buildings/{building_id}` — `CAN_DELETE_BUILDING`

Cascade-deletes all units, sensors, and thresholds belonging to this building.

**Response `200`:** deleted `BuildingResponse`.

---

### Units

A unit is an apartment or commercial space within a building.

#### `POST /units` — `CAN_CREATE_UNIT`

**Request body:**
```json
{
  "building_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "unit_number": "42",
  "floor": 5,
  "owner_name": "Иванов И.И."
}
```

**Response `201`:** `UnitResponse`

---

#### `GET /units/{unit_id}` — `CAN_READ_UNIT`

**Response `200`:**
```json
{
  "unit_id": "...",
  "building_id": "...",
  "unit_number": "42",
  "floor": 5,
  "owner_name": "Иванов И.И."
}
```

---

#### `PUT /units/{unit_id}` — `CAN_UPDATE_UNIT`

**Request body:**
```json
{
  "unit_number": "42a",
  "floor": 5,
  "owner_name": "Петров П.П."
}
```

---

#### `DELETE /units/{unit_id}` — `CAN_DELETE_UNIT`

Cascade-deletes sensors and thresholds attached to this unit.

---

### Sensors

A sensor measures energy consumption. Two attachment modes exist:

- **COMMON** — attached to a building; measures total incoming energy.
- **INDIVIDUAL** — attached to a unit; measures that unit's consumption.

The energy balance calculation requires exactly one COMMON sensor per building.

#### `POST /sensors` — `CAN_CREATE_SENSOR`

**Request body:**
```json
{
  "serial_number": "SN-001",
  "model": "Energomera CE301",
  "calibration_date": "2025-01-15",
  "sensor_type": "INDIVIDUAL",
  "building_id": null,
  "unit_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

| Field | Type | Notes |
|---|---|---|
| `sensor_type` | `COMMON` \| `INDIVIDUAL` | Determines which FK is required |
| `building_id` | UUID \| null | Required when `sensor_type=COMMON` |
| `unit_id` | UUID \| null | Required when `sensor_type=INDIVIDUAL` |

Setting both or neither `building_id` / `unit_id` returns **422**.

**Response `201`:** `SensorResponse`

---

#### `GET /sensors/{sensor_id}` — `CAN_READ_SENSOR`

**Response `200`:**
```json
{
  "sensor_id": "...",
  "serial_number": "SN-001",
  "model": "Energomera CE301",
  "calibration_date": "2025-01-15",
  "sensor_type": "INDIVIDUAL",
  "building_id": null,
  "unit_id": "..."
}
```

---

#### `PUT /sensors/{sensor_id}` — `CAN_UPDATE_SENSOR`

Only metadata fields are updatable; the attachment target (`building_id` / `unit_id`) cannot change after creation.

**Request body:**
```json
{
  "serial_number": "SN-001-R",
  "model": "Energomera CE303",
  "calibration_date": "2026-01-15"
}
```

---

#### `DELETE /sensors/{sensor_id}` — `CAN_DELETE_SENSOR`

Cascade-deletes thresholds and historical metric rows.

---

### Thresholds

A threshold defines an energy consumption limit for a specific sensor, tariff zone, and threshold type. When a metric exceeds the limit, the workers service raises an incident.

#### `POST /thresholds` — `CAN_CREATE_THRESHOLD`

**Request body:**
```json
{
  "sensor_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "limit_value": 150.0,
  "threshold_type": "DAILY",
  "tariff_zone": "PEAK"
}
```

| Field | Type | Notes |
|---|---|---|
| `limit_value` | float | kWh limit |
| `threshold_type` | enum | e.g. `DAILY`, `MONTHLY` |
| `tariff_zone` | enum | e.g. `PEAK`, `SEMI_PEAK`, `NIGHT` |

**Response `201`:** `ThresholdResponse`

---

#### `GET /thresholds/{threshold_id}` — `CAN_READ_THRESHOLD`

**Response `200`:**
```json
{
  "threshold_id": "...",
  "sensor_id": "...",
  "limit_value": 150.0,
  "threshold_type": "DAILY",
  "tariff_zone": "PEAK"
}
```

---

#### `PUT /thresholds/{threshold_id}` — `CAN_UPDATE_THRESHOLD`

Only the numeric limit can be changed.

**Request body:**
```json
{
  "limit_value": 120.0
}
```

---

#### `DELETE /thresholds/{threshold_id}` — `CAN_DELETE_THRESHOLD`

---

### Energy Balances

Pre-computed daily energy loss reports per building. Records are written by the nightly scheduled job and are read-only through the API.

#### `GET /energy-balances` — `CAN_READ_ENERGY_BALANCE`

**Query parameters:**

| Param | Type | Required | Notes |
|---|---|---|---|
| `building_id` | UUID | Yes | Filter by building |
| `date_from` | datetime (ISO 8601) | No | Inclusive start of range |
| `date_to` | datetime (ISO 8601) | No | Inclusive end of range |

**Example:**
```
GET /energy-balances?building_id=3fa85f64-...&date_from=2026-01-01T00:00:00Z&date_to=2026-02-01T00:00:00Z
```

**Response `200`:**
```json
[
  {
    "balance_id": "...",
    "building_id": "...",
    "period_start": "2026-01-01T00:00:00+00:00",
    "period_end": "2026-01-02T00:00:00+00:00",
    "loss_kwh": 12.4,
    "loss_percent": 3.8
  }
]
```

`loss_kwh` is the difference between what the COMMON sensor recorded and the sum of all INDIVIDUAL sensors. `loss_percent` is relative to the COMMON reading.

---

## Domain Model

```
Building 1──* Unit 1──* Sensor(INDIVIDUAL) 1──* Threshold
Building 1──* Sensor(COMMON)              1──* Threshold
Building 1──* EnergyBalance
Sensor    1──* Metric ──────────────────────> AverageLoad
```

- Deleting a **Building** cascades to Units → Sensors → Thresholds.
- Deleting a **Unit** cascades to its Sensors → Thresholds.
- Deleting a **Sensor** cascades to Thresholds and Metric rows.
- **Incidents** reference Thresholds and PeakLoad records with `SET NULL` — the audit log is preserved even after threshold deletion.

---

## Scheduled Jobs

Both jobs are registered with APScheduler at application startup.

### Average Load — every hour at :05

Reads the last hour of raw metrics for every sensor and writes a single `AverageLoad` row per sensor with `avg_value`, `min_value`, `max_value`, and `measurement_count`.

Fired at `:05` to avoid the `:00` thundering-herd; gives NATS consumers time to flush recent metrics.

### Energy Balance — daily at 00:10 UTC

For each building that has a COMMON sensor, computes:

```
loss_kwh    = common_total - sum(individual_totals)
loss_percent = loss_kwh / common_total * 100
```

The result is written as an `EnergyBalance` row for yesterday's 24-hour period.

Fired at `00:10` to allow the previous day's metrics to be fully flushed before aggregation.

---

## Error Responses

All error bodies follow the same schema:

```json
{
  "detail": "Human-readable error message"
}
```

| Status | Cause |
|---|---|
| 401 | Missing or invalid `Authorization` header / expired token / wrong password |
| 403 | Authenticated but insufficient role permissions |
| 404 | Requested resource does not exist |
| 409 | Conflict — e.g. email already registered |
| 422 | Validation error — e.g. sensor attached to both building and unit |

---

## Prometheus Metrics

Metrics are exposed at `GET /metrics` (no auth required) by `prometheus-fastapi-instrumentator`. Standard HTTP metrics are collected automatically: request count, latency histograms, and in-flight requests, all labelled by method and path template.
