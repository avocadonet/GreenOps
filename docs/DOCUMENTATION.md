# GreenOps — Technical Documentation

> Smart City Energy Consumption Monitoring & Optimization Platform

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Installation & Setup](#3-installation--setup)
4. [API Reference](#4-api-reference)
5. [Key Workflows & Examples](#5-key-workflows--examples)
6. [Configuration Reference](#6-configuration-reference)
7. [Folder Structure](#7-folder-structure)
8. [Contributing Guide](#8-contributing-guide)
9. [Known Limitations & TODOs](#9-known-limitations--todos)

---

## 1. Project Overview

GreenOps is an event-driven microservices platform for real-time energy consumption monitoring and optimization in smart cities. It ingests telemetry from thousands of IoT sensors, detects anomalies (spikes, leaks, overloads), computes energy balance reports, and exposes the data through a REST API and a Vue 3 dashboard.

**Core problems it solves:**

- Continuous ingestion of high-frequency sensor telemetry without blocking API serving
- Real-time spike detection and incident creation across heterogeneous sensor types
- Energy loss computation (difference between common building-level consumption and the sum of individual unit consumption)
- Role-based access control with both global roles and per-organization roles so building owners, administrators, and redactors each see only what they need

**Target audience:** Back-end and full-stack engineers studying production-grade Python microservices; smart city / energy management operators.

---

## 2. Architecture Overview

### 2.1 Services

| Service | Responsibility |
|---|---|
| **crud** | Control-plane REST API — manage organizations, buildings, units, sensors, thresholds, users; schedule background analytics jobs |
| **workers** | Data-plane — consume Kafka events, persist metrics, detect spikes, publish incidents |
| **shared** | Python package containing shared domain entities, DTOs, SQLAlchemy models, and Alembic migrations |
| **crudx** | Internal CRUD helper library on top of SQLAlchemy 2.0 async |
| **frontend** | Vue 3 SPA (Chart.js dashboards) |
| **gateway** | Nginx reverse proxy routing `/*` to the API and `/` to the SPA |
| **monitoring** | Prometheus + Grafana + cAdvisor + exporters |

### 2.2 Data Flow

```
IoT Sensors / simulator.py
        │
        │  Kafka topic: telemetry.raw
        ▼
┌───────────────┐
│   workers     │──── TelemetryService.process()
│  (FastStream) │         │
└───────────────┘         ├─ persist Metric to PostgreSQL
                          ├─ SpikeDetector.check()
                          │       │
                          │       └─ spike detected?
                          │               │  Kafka topic: incidents.created
                          │               ▼
                          │       on_incident_created()
                          │       (log / notify)
                          │
┌───────────────────────────────────────────┐
│        PostgreSQL  (shared schema)        │
│  organizations · buildings · units        │
│  sensors · metrics · thresholds           │
│  energy_balances · users …                │
└──────────────────┬────────────────────────┘
                   │
         ┌─────────┴──────────┐
         │      crud          │  FastAPI + Dishka DI
         │  (control plane)   │  ├─ REST CRUD endpoints
         │                    │  ├─ JWT auth / RBAC
         │                    │  └─ APScheduler jobs
         └────────────────────┘  ┌ AverageLoadService (hourly :05)
                   │             └ EnergyBalanceService (daily 00:10)
                   │
              Nginx (port 80)
                   │
              Vue 3 SPA / Grafana
```

### 2.3 Layered Design (crud service)

Each vertical (organization, building, sensor, unit, etc.) follows the same three-layer pattern:

```
infrastructure/api/<domain>/router.py   ← HTTP boundary (FastAPI)
application/<domain>/service.py         ← Use-cases / business logic
domain/<domain>/repository.py           ← Abstract repository (ABC)
infrastructure/db/<domain>/repository.py← Concrete SQLAlchemy implementation
```

Dependency injection (Dishka) wires the concrete implementations to the ABCs at startup, so the application layer never imports infrastructure.

### 2.4 Multi-Tenancy

Resources (buildings, units, sensors, thresholds) each carry a nullable `organization_id` FK. When it is set, permission checks are performed against the requesting user's role within that organization (`UserOrganizationRoleModel`). When it is `null` the check falls back to the user's global role. This allows a gradual migration from a flat global role model to full multi-tenancy.

### 2.5 Key Design Patterns

- **Clean / Hexagonal Architecture** — domain layer has zero infrastructure imports
- **Repository Pattern** — each aggregate has an ABC repository; infrastructure implements it
- **DTO / Entity separation** — `CreateXyzDTO` for input, `Xyz` dataclass entity for domain use, Pydantic schema for HTTP serialization
- **CQRS-lite** — reads return entities; writes accept DTOs
- **Dependency Injection** — Dishka container with `Application` and `Request` scopes
- **Decorator-based CRUD** — `crudx` decorators (`@decorators.create`, `@decorators.read`, …) handle mapping and error translation

---

## 3. Installation & Setup

### 3.1 Prerequisites

| Tool | Version |
|---|---|
| Docker & Docker Compose | >= 24 |
| Python | 3.12 (only needed for the simulator or local dev) |
| Poetry | >= 1.8 |

### 3.2 Running the Full Stack (Docker)

```bash
# 1. Clone the repo
git clone <repo-url> GreenOps && cd GreenOps

# 2. Copy and fill environment variables (see §6 for all variables)
cp .env.example .env   # if present, otherwise create manually

# 3. Start every service
docker compose up --build

# 4. Verify
curl http://localhost/api/docs      # FastAPI Swagger UI (via Nginx)
open http://localhost               # Vue 3 frontend
open http://localhost:3000          # Grafana  (admin / admin)
open http://localhost:9090          # Prometheus
```

The `migrations` container runs `alembic upgrade head` once on startup, then exits. All other services wait for PostgreSQL to be healthy before starting.

### 3.3 Running Services Locally (without Docker)

```bash
# Shared kernel (install as editable)
cd services/shared && poetry install

# crudx (install as editable)
cd ../crudx && poetry install

# CRUD service
cd ../crud
poetry install
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/greenops"
export JWT_SECRET_KEY="supersecret"
poetry run uvicorn infrastructure.api.app:create_app --factory \
  --host 0.0.0.0 --port 8000 --reload

# Workers service
cd ../workers
poetry install
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/greenops"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
poetry run python main.py
```

### 3.4 Running Migrations Manually

```bash
cd services/shared
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/greenops"
poetry run alembic -c src/shared/migrations/alembic.ini upgrade head
```

### 3.5 Running the Telemetry Simulator

```bash
pip install aiokafka  # or use the provided environment

# Default mode (10 % of messages are spikes)
python simulator.py --sensor-id <uuid> --bootstrap-servers localhost:9092

# All normal readings
python simulator.py --sensor-id <uuid> --mode normal --rate 5

# All spikes
python simulator.py --sensor-id <uuid> --mode spike --threshold 300
```

---

## 4. API Reference

Base URL: `http://localhost/api` (through Nginx) or `http://localhost:8000` (direct)

Interactive docs: `GET /docs` (Swagger UI), `GET /redoc`

All endpoints are versioned under `/v1`: `GET /api/v1/buildings`, etc.

### 4.1 Authentication

All non-auth endpoints require a Bearer JWT in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

#### `POST /auth/register`

Create a new user account.

**Request body**

| Field | Type | Description |
|---|---|---|
| `email` | `EmailStr` | Unique user email |
| `password` | `str` | Plain-text password (hashed with bcrypt) |
| `fullname` | `str` | Display name |

**Response `201`**

```json
{
  "message": "User registered. Activate your account to log in.",
  "user_id": 42,
  "email": "user@example.com"
}
```

**Errors**

| Code | Condition |
|---|---|
| `409` | Email already registered (`UserAlreadyExistsError`) |

---

#### `POST /auth/login`

Authenticate and obtain a token pair.

**Request body**

| Field | Type |
|---|---|
| `email` | `EmailStr` |
| `password` | `str` |

**Response `200`**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user_id": 42,
  "email": "user@example.com"
}
```

**Errors**

| Code | Condition |
|---|---|
| `401` | Wrong credentials (`InvalidCredentialsError`) |

---

### 4.2 Organizations

#### `GET /organizations` — List

**Permission:** `CAN_READ_ORGANIZATION` (global role)

**Query parameters:**

| Param | Type | Default |
|---|---|---|
| `page` | `int` | `1` |
| `page_size` | `int` | `20` |

**Response `200`** — `PaginatedResponse[OrganizationResponse]`

---

#### `POST /organizations` — Create

**Permission:** `CAN_CREATE_ORGANIZATION` (global role — SUPER_* only)

The `owner_id` is set automatically from the authenticated user's identity.

**Request body**

| Field | Type | Required |
|---|---|---|
| `name` | `str` | Yes |
| `description` | `str \| null` | No |
| `contact_email` | `str \| null` | No |

**Response `201`** — `OrganizationResponse`

```json
{
  "id": 1,
  "name": "Acme Corp",
  "owner_id": 42,
  "description": "Main organization",
  "contact_email": "ops@acme.io",
  "created_at": "2026-05-02T12:00:00Z"
}
```

---

#### `GET /organizations/{org_id}` — Read

**Permission:** `CAN_READ_ORGANIZATION` (org-scoped — `ORGANIZATION_OWNER` or higher within the org)

**Errors:** `404` if not found

---

#### `PUT /organizations/{org_id}` — Update

**Permission:** `CAN_UPDATE_ORGANIZATION` (org-scoped)

**Request body** — same fields as Create (all optional, `name` required)

**Response `200`** — `OrganizationResponse`

---

#### `DELETE /organizations/{org_id}` — Delete

**Permission:** `CAN_DELETE_ORGANIZATION` (org-scoped)

**Response `200`** — deleted `OrganizationResponse`

---

### 4.3 Buildings

#### `GET /buildings` — List

**Permission:** `CAN_READ_BUILDING`  
When `organization_id` is provided the check is org-scoped; otherwise global.

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `organization_id` | `int \| null` | Filter by organization |
| `page` | `int` | Default `1` |
| `page_size` | `int` | Default `20`, max `100` |

**Response `200`** — `PaginatedResponse[BuildingResponse]`

---

#### `POST /buildings` — Create

**Permission:** `CAN_CREATE_BUILDING`  
When `organization_id` is provided the check is org-scoped; otherwise global.

**Request body**

| Field | Type | Values |
|---|---|---|
| `address` | `str` | Free text |
| `building_type` | `BuildingType` | `RESIDENTIAL`, `INDUSTRIAL` |
| `total_area` | `float` | Square metres |
| `organization_id` | `int \| null` | Organization this building belongs to |

**Response `201`** — `BuildingResponse`

```json
{
  "building_id": "3fa85f64-...",
  "address": "Main St 1",
  "building_type": "RESIDENTIAL",
  "total_area": 1200.5,
  "organization_id": 1
}
```

---

#### `GET /buildings/{building_id}` — Read

**Permission:** `CAN_READ_BUILDING` (org-scoped if building has `organization_id`)

**Response `200`** — `BuildingResponse`

**Errors:** `404` if not found

---

#### `PUT /buildings/{building_id}` — Update

**Permission:** `CAN_UPDATE_BUILDING` (org-scoped if building has `organization_id`)

**Request body**

| Field | Type |
|---|---|
| `address` | `str` |
| `total_area` | `float` |

**Response `200`** — `BuildingResponse`

---

#### `DELETE /buildings/{building_id}` — Delete

**Permission:** `CAN_DELETE_BUILDING` (org-scoped if building has `organization_id`)

**Response `200`** — deleted `BuildingResponse`

---

### 4.4 Units

#### `GET /units` — List

**Permission:** `CAN_READ_UNIT`  
When `organization_id` is provided the check is org-scoped; otherwise global.

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `building_id` | `UUID \| null` | Filter by building |
| `organization_id` | `int \| null` | Filter by organization |
| `page` | `int` | Default `1` |
| `page_size` | `int` | Default `20`, max `100` |

---

#### `POST /units` — Create

**Permission:** `CAN_CREATE_UNIT` (org-scoped if `organization_id` set)

**Request body**

| Field | Type | Description |
|---|---|---|
| `building_id` | `UUID` | Parent building |
| `unit_number` | `str` | Apartment / office number |
| `floor` | `int` | Floor number |
| `owner_name` | `str` | Tenant / owner name |
| `organization_id` | `int \| null` | Organization this unit belongs to |

**Response `201`** — `UnitResponse`

---

`GET /units/{unit_id}`, `PUT /units/{unit_id}`, `DELETE /units/{unit_id}` follow the same pattern as Buildings. Permission checks are org-scoped when the unit has `organization_id`.

---

### 4.5 Sensors

#### `GET /sensors` — List

**Permission:** `CAN_READ_SENSOR`  
When `organization_id` is provided the check is org-scoped; otherwise global.

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `organization_id` | `int \| null` | Filter by organization |
| `page` | `int` | Default `1` |
| `page_size` | `int` | Default `20`, max `100` |

---

#### `POST /sensors` — Create

**Permission:** `CAN_CREATE_SENSOR` (org-scoped if `organization_id` set)

**Request body**

| Field | Type | Description |
|---|---|---|
| `serial_number` | `str` | Device serial |
| `model` | `str` | Device model |
| `calibration_date` | `date` | ISO-8601 date |
| `sensor_type` | `SensorType` | `COMMON` or `INDIVIDUAL` |
| `building_id` | `UUID \| null` | Required for `COMMON` sensors |
| `unit_id` | `UUID \| null` | Required for `INDIVIDUAL` sensors |
| `organization_id` | `int \| null` | Organization this sensor belongs to |

> **Attachment constraint (XOR):** exactly one of `building_id` / `unit_id` must be set.  
> `COMMON` sensors attach to a building; `INDIVIDUAL` sensors attach to a unit.  
> Violating this constraint returns `422 SensorAttachmentException`.

**Response `201`** — `SensorResponse`

---

`GET /sensors/{sensor_id}`, `PUT /sensors/{sensor_id}`, `DELETE /sensors/{sensor_id}` follow the same pattern as Buildings. Permission checks are org-scoped when the sensor has `organization_id`.

Updatable fields: `serial_number`, `model`, `calibration_date`.  
Sensor type and attachment cannot be changed after creation.

---

### 4.6 Thresholds

#### `GET /thresholds` — List

**Permission:** `CAN_READ_THRESHOLD`

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `sensor_id` | `UUID \| null` | Filter by sensor |
| `organization_id` | `int \| null` | Filter by organization |
| `page` | `int` | Default `1` |
| `page_size` | `int` | Default `20`, max `100` |

---

#### `POST /thresholds` — Create

**Permission:** `CAN_CREATE_THRESHOLD` (org-scoped if `organization_id` set)

**Request body**

| Field | Type | Values |
|---|---|---|
| `sensor_id` | `UUID` | Parent sensor |
| `limit_value` | `float` | Threshold value |
| `threshold_type` | `ThresholdType` | `UPPER`, `LOWER` |
| `tariff_zone` | `TariffZone` | `DAY`, `NIGHT` |
| `organization_id` | `int \| null` | Organization this threshold belongs to |

---

`GET /thresholds/{threshold_id}`, `PUT /thresholds/{threshold_id}`, `DELETE /thresholds/{threshold_id}` follow the same pattern.

Updatable fields: `limit_value`.

---

### 4.7 Energy Balances

#### `GET /energy-balances`

**Permission:** `CAN_READ_ENERGY_BALANCE`  
The check is org-scoped when the referenced building belongs to an organization; otherwise global.

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `building_id` | `UUID` | Required — filter by building |
| `date_from` | `datetime` | Range start (ISO-8601) |
| `date_to` | `datetime` | Range end (ISO-8601) |

**Response `200`** — `list[EnergyBalanceResponse]`

```json
[{
  "balance_id": "...",
  "building_id": "...",
  "period_start": "2024-01-01T00:00:00",
  "period_end":   "2024-01-02T00:00:00",
  "loss_kwh":     45.3,
  "loss_percent": 3.8
}]
```

Energy balances are computed automatically by a background job (daily at 00:10). They are read-only through the API.

---

### 4.8 Error Response Shape

All error responses follow this envelope:

```json
{ "detail": "Human-readable message" }
```

| HTTP | Exception class | Trigger |
|---|---|---|
| `400` | — | Validation errors (Pydantic) |
| `401` | `InvalidCredentialsError` | Wrong credentials or expired token |
| `403` | `UserNotValidated` | Valid token but insufficient permissions |
| `404` | `EntityNotFoundException` | Entity with given ID not found |
| `409` | `UserAlreadyExistsError` | Email already registered |
| `422` | `SensorAttachmentException` | XOR attachment constraint violated |

---

### 4.9 Permission Matrix

#### Global roles

| Permission | PUBLIC | OWNER | REDACTOR | ADMIN | SUPER_* |
|---|---|---|---|---|---|
| Read building/unit/sensor/threshold | — | ✓ | ✓ | ✓ | ✓ |
| Create/Update/Delete threshold | — | — | ✓ | ✓ | ✓ |
| Full CRUD building/unit/sensor | — | — | — | ✓ | ✓ |
| Read energy balance | — | ✓ | ✓ | ✓ | ✓ |
| Read/Update/Delete organization | — | — | — | — | ✓ |
| Create organization | — | — | — | — | ✓ |
| User & role management | — | — | — | — | ✓ |

#### Organization-scoped role (`ORGANIZATION_OWNER`)

Assigned per-organization via `UserOrganizationRoleModel`. When a resource belongs to an organization, the permission check uses this role instead of the global role.

| Permission | ORGANIZATION_OWNER |
|---|---|
| Read/Update/Delete organization | ✓ |
| Create organization | — |
| Full CRUD building/unit/sensor/threshold | ✓ |
| Read energy balance | ✓ |
| User & role management | — |

---

### 4.10 Internal Module Reference

#### `application/auth/services.py` — `AuthService`

| Method | Signature | Description |
|---|---|---|
| `login` | `(AuthenticateUserDto) → (User, TokenPairDto)` | Verify bcrypt password, create token pair |
| `register` | `(RegisterUserDto) → User` | Hash password, create user |
| `authorize` | `(TokenInfoDto) → User` | Validate JWT subject, return active user |

#### `application/<domain>/service.py`

Each service exposes `create / read / list_all / update / delete` methods that accept a `User` for permission checks plus DTOs, delegate to the repository, and raise domain exceptions on errors.

All services support org-scoped permission checks: when the relevant `organization_id` is not `None`, permissions are evaluated against the user's `ORGANIZATION_OWNER` role for that org. Otherwise the global role is used.

`AverageLoadService.run_hourly()` — computes `mean(metric.value)` per sensor over the previous hour and persists an `AverageLoad` record.

`EnergyBalanceService.run_daily()` — for each building computes:

```
loss_percent = (common_kwh - sum(individual_kwh)) / common_kwh * 100
```

and persists an `EnergyBalance` record.

`EnergyBalanceService.list_by_building(user, building_id, date_from, date_to)` — reads the building to resolve its `organization_id`, performs org-scoped or global `CAN_READ_ENERGY_BALANCE` check, then queries the repository.

#### `workers/src/telemetry.py` — `TelemetryService`

| Method | Description |
|---|---|
| `process(dto: CreateMetricDTO)` | Persist metric; run `SpikeDetector`; if spike, publish `incidents.created` |

#### `workers/src/spike_detector.py` — `SpikeDetector`

Compares `metric.value` against the sensor's configured `Threshold.limit_value` for the matching `TariffZone`. Returns `True` (spike) when the value exceeds an `UPPER` threshold or falls below a `LOWER` threshold.

#### `crudx` — `AsyncSqlAlchemyGateway`

| Method | Description |
|---|---|
| `select_by_id(id)` | `SELECT … WHERE pk = id` |
| `select_by_fields_all(**filters)` | `SELECT … WHERE field = value …` |
| `insert(dto)` | `INSERT … RETURNING *` |
| `update(entity)` | `UPDATE … SET … WHERE pk = id` |
| `delete(entity)` | `DELETE … WHERE pk = id` |

Decorators (`@decorators.create`, etc.) wrap repository methods to handle `IntegrityError → EntityAlreadyExistsException` and `NoResultFound → EntityNotFoundException` automatically.

---

## 5. Key Workflows & Examples

### 5.1 Register → Login → Authenticated Request

```bash
# 1. Register
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ops@city.io","password":"s3cret","fullname":"Ops User"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ops@city.io","password":"s3cret"}' \
  | jq -r '.access_token')

# 3. Use token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost/api/v1/buildings/<uuid>
```

### 5.2 Create an Organization and Provision Resources Under It

```bash
AUTH="Authorization: Bearer $TOKEN"

# 1. Create organization (requires SUPER_* role)
ORG=$(curl -s -X POST http://localhost/api/v1/organizations \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp","contact_email":"ops@acme.io"}' \
  | jq -r '.id')

# 2. Create building inside organization
BLD=$(curl -s -X POST http://localhost/api/v1/buildings \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"address\":\"Main St 1\",\"building_type\":\"RESIDENTIAL\",\"total_area\":1200,\"organization_id\":$ORG}" \
  | jq -r '.building_id')

# 3. Create unit inside building
UNIT=$(curl -s -X POST http://localhost/api/v1/units \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"building_id\":\"$BLD\",\"unit_number\":\"101\",\"floor\":1,\"owner_name\":\"Alice\",\"organization_id\":$ORG}" \
  | jq -r '.unit_id')

# 4. Create a COMMON (building-level) sensor
BSENSOR=$(curl -s -X POST http://localhost/api/v1/sensors \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"serial_number\":\"SN-001\",\"model\":\"EM-3000\",\"calibration_date\":\"2024-01-01\",\"sensor_type\":\"COMMON\",\"building_id\":\"$BLD\",\"organization_id\":$ORG}" \
  | jq -r '.sensor_id')

# 5. Create an INDIVIDUAL (unit-level) sensor
USENSOR=$(curl -s -X POST http://localhost/api/v1/sensors \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"serial_number\":\"SN-002\",\"model\":\"EM-1000\",\"calibration_date\":\"2024-01-01\",\"sensor_type\":\"INDIVIDUAL\",\"unit_id\":\"$UNIT\",\"organization_id\":$ORG}" \
  | jq -r '.sensor_id')

# 6. Set an UPPER threshold for the building sensor (daytime)
curl -s -X POST http://localhost/api/v1/thresholds \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"sensor_id\":\"$BSENSOR\",\"limit_value\":500,\"threshold_type\":\"UPPER\",\"tariff_zone\":\"DAY\",\"organization_id\":$ORG}"
```

### 5.3 Send Telemetry

```bash
python simulator.py \
  --sensor-id "$BSENSOR" \
  --bootstrap-servers localhost:9092 \
  --mode default \
  --rate 2
```

The workers service consumes `telemetry.raw`, persists each `Metric`, and publishes an incident to `incidents.created` when the value crosses a threshold.

### 5.4 Query Energy Balances

Energy balances are computed automatically at `00:10` daily. You can also trigger them manually for testing:

```python
# Inside the running crud container
from application.energy_balance.service import EnergyBalanceService
await service.run_daily()
```

Then query:

```bash
curl -H "$AUTH" \
  "http://localhost/api/v1/energy-balances?building_id=$BLD&date_from=2024-01-01T00:00:00&date_to=2024-01-02T00:00:00"
```

---

## 6. Configuration Reference

### 6.1 `crud` service — environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | asyncpg URL, e.g. `postgresql+asyncpg://user:pass@host/db` |
| `JWT_SECRET_KEY` | Yes | — | Secret used to sign/verify JWTs |

### 6.2 `workers` service — environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | Same asyncpg URL as crud service |
| `KAFKA_BOOTSTRAP_SERVERS` | Yes | — | Comma-separated list, e.g. `kafka:9092` |

### 6.3 JWT settings (`application/auth/tokens/config.py`)

| Field | Default | Description |
|---|---|---|
| `access_token_expire_minutes` | `30` | Access token lifetime in minutes |
| `refresh_token_expire_days` | `7` | Refresh token lifetime in days |
| `algorithm` | `"HS256"` | JWT signing algorithm |

### 6.4 APScheduler jobs (`infrastructure/scheduler/jobs.py`)

| Job | Schedule | Description |
|---|---|---|
| `run_average_load` | `*/1 * * * *` at `:05` past each hour | Compute per-sensor hourly averages |
| `run_energy_balance` | `0 0 * * *` at `00:10` | Compute daily building energy loss |

### 6.5 Database connection pool (`infrastructure/db/postgres.py`)

| Parameter | Value | Notes |
|---|---|---|
| `pool_size` | `10` | SQLAlchemy async engine pool size |
| `expire_on_commit` | `False` | Session maker setting to keep objects accessible after commit |

### 6.6 Prometheus endpoint

Exposed automatically by `prometheus-fastapi-instrumentator` at `GET /metrics` on the crud service.

---

## 7. Folder Structure

```
GreenOps/
├── simulator.py              # CLI tool to publish fake sensor telemetry to Kafka
├── docker-compose.yml        # Full-stack service orchestration
├── monitoring/
│   └── prometheus.yml        # Prometheus scrape config (crud, cadvisor, exporters)
├── nginx/
│   └── nginx.conf            # Reverse proxy: /api → crud:8000, / → frontend:3000
├── assets/                   # Architecture diagrams
├── docs/                     # Project documentation
├── frontend/                 # Vue 3 SPA
│   ├── src/api/              # Axios client wrappers
│   ├── src/components/       # Reusable UI components
│   ├── src/composables/      # Vue composables (useMetrics, useSensors, …)
│   └── src/views/            # Page-level components
│
└── services/
    ├── shared/               # Shared Python kernel (installed as a package)
    │   └── src/shared/
    │       ├── enums.py      # All domain enumerations
    │       ├── exceptions.py # Base exception hierarchy
    │       ├── entities/     # Dataclass domain objects (pure Python, no ORM)
    │       ├── dtos/         # Input / output transfer objects
    │       ├── db/           # SQLAlchemy mapped models + __init__ imports for Alembic
    │       └── migrations/   # Alembic env + versioned migration scripts
    │
    ├── crudx/                # Internal async SQLAlchemy CRUD library
    │   └── src/crudx/sa/
    │       ├── gateway/      # AsyncSqlAlchemyGateway (core CRUD methods)
    │       ├── decorators.py # @create/@read/@update/@delete with error mapping
    │       ├── config.py     # SqlalchemyConfig[CreateDTO, Entity, Model]
    │       └── transaction.py# AsyncTransactionsDatabaseGateway base class
    │
    ├── crud/                 # Control-plane REST API service
    │   ├── main.py           # Entry point: build container, register scheduler, run uvicorn
    │   └── src/
    │       ├── domain/       # ABCs (repositories) + domain exceptions
    │       │   ├── users/    # User-specific entities, enums, and repository ABCs
    │       │   └── organization/ # Organization repository ABC + exceptions
    │       ├── application/  # Use cases and services (no infrastructure imports)
    │       │   ├── auth/     # JWT / bcrypt gateways ABCs + permission system
    │       │   └── <domain>/ # BuildingService, OrganizationService, etc.
    │       └── infrastructure/
    │           ├── api/      # FastAPI routers, Pydantic schemas, DI dependencies
    │           ├── auth/     # Concrete JWT + bcrypt implementations
    │           ├── db/       # Concrete SQLAlchemy repositories + mappers
    │           ├── configs/  # Config dataclass (reads env vars)
    │           ├── providers/# Dishka providers (container wiring)
    │           └── scheduler/# APScheduler job registration
    │
    └── workers/              # Data-plane Kafka consumer service
        ├── main.py           # Entry point: build FastStream app, run
        └── src/
            ├── kafka_app.py      # FastStream + KafkaBroker factory
            ├── kafka_consumers.py# @subscriber handlers for telemetry.raw, incidents.created
            ├── telemetry.py      # TelemetryService: persist metric + detect spike
            ├── spike_detector.py # Threshold comparison logic
            ├── config.py         # Config dataclass (DATABASE_URL, KAFKA_BOOTSTRAP_SERVERS)
            ├── database.py       # Async engine + session maker
            └── container.py      # Dishka container for workers
```

---

## 8. Contributing Guide

### 8.1 Running Tests

```bash
# crudx unit + integration tests (require a live PostgreSQL)
cd services/crudx
DATABASE_URL="postgresql+asyncpg://user:pass@localhost/greenops_test" \
  poetry run pytest

# crud service unit tests
cd services/crud
poetry run pytest src/tests/

# workers unit tests
cd services/workers
poetry run pytest src/tests/
```

### 8.2 Adding a New Domain Entity

1. **Shared kernel** (`services/shared/src/shared/`)
   - Add dataclass to `entities/<domain>.py`
   - Add DTOs to `dtos/<domain>.py`
   - Add SQLAlchemy model to `db/<domain>.py` and re-export it in `db/__init__.py`
   - Generate an Alembic migration: `alembic revision --autogenerate -m "add <domain>"`

2. **Domain layer** (`services/crud/src/domain/<domain>/`)
   - Add `repository.py` with an ABC `XyzRepository`
   - Add `exceptions.py` with `XyzNotFoundException` etc.

3. **Application layer** (`services/crud/src/application/<domain>/`)
   - Add `service.py` with `XyzService` (depends on the ABC via constructor injection)
   - Inject `RoleGetter` for permission checks; use `_check(user, ...)` for global checks and `_check_org(user, organization_id, ...)` for org-scoped checks

4. **Infrastructure layer**
   - `infrastructure/db/<domain>/repository.py` — concrete implementation using `crudx`
   - `infrastructure/db/<domain>/mappers.py` — `Adaptix` `ConversionRetort` mappings
   - `infrastructure/api/<domain>/schemas.py` — Pydantic request / response models
   - `infrastructure/api/<domain>/router.py` — FastAPI router with permission checks via service
   - Register the router in `infrastructure/api/router.py`
   - Wire the repository in `infrastructure/providers/repositories.py`
   - Wire the service in `infrastructure/providers/services.py`

### 8.3 Code Style

- Python 3.12 type hints throughout; use `from __future__ import annotations` where helpful
- `dataclass` for domain entities and DTOs; Pydantic `BaseModel` only at the HTTP boundary
- No business logic in routers; no infrastructure imports in domain or application layers
- `async def` for all I/O-bound operations
- DB-layer mappers use `Adaptix`; API-layer mappers use manual field-by-field mapping

### 8.4 Adding a Kafka Consumer

1. Define a new `@router.subscriber("<topic>")` handler in `workers/src/kafka_consumers.py`
2. Add the topic to the workers `Config` if it needs to be configurable
3. Inject any required services via `FromDishka[...]` and register them in `workers/src/container.py`

---

## 9. Known Limitations & TODOs

### Security

- **JWT refresh token rotation is not implemented.** Refresh tokens are issued but there is no `/auth/refresh` endpoint to exchange them. Expired access tokens cannot be renewed without re-logging in.
- **No rate limiting** on authentication endpoints — brute-force attacks on `/auth/login` are not mitigated at the application layer (Nginx could provide this).
- **`JWT_SECRET_KEY` must be set as an environment variable** — there is no default fallback, which is correct, but the application will crash at startup without it. Document this prominently in deployment runbooks.

### Features

- `UserActivationToken` and `TelegramToken` entities exist in the domain but no activation / Telegram-linking endpoints are implemented yet.
- `PeakLoad` entity and table exist but there is no service or endpoint to query peak loads directly.
- The `incidents.created` Kafka consumer (`on_incident_created`) only logs the event — no notifications are sent to users.
- `UserNotificationSendToEnum` (EMAIL, TELEGRAM) is defined but notification dispatch is not implemented.
- Redis is referenced in the README as "planned" but is not used anywhere in the current codebase.
- There are no endpoints for managing organization membership (assigning / removing `UserOrganizationRole`). Users must be granted org roles directly in the database.

### Operational

- Alembic migrations are defined under `services/shared`, which means both `crud` and `workers` must share the same database schema version. There is no mechanism to prevent a service from starting against an incompatible schema version (beyond the `migrations` container in Docker Compose running before the others).
- `pool_size=10` is hard-coded in `infrastructure/db/postgres.py`; it is not configurable via environment variables.
- The APScheduler jobs acquire a new Dishka request container on each tick but there is no explicit cleanup / scope exit; a memory leak is possible under high job frequency if the container is not correctly closed.
