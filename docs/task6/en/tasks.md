# GreenOps — Technical Task Breakdown

> Assumed team: Backend Dev (BE), Frontend Dev (FE), DB/DevOps Engineer (DevOps), QA/Analyst (QA).  
> Backend Dev doubles as architect in Phase 1–2.  
> Project start: 01.04.2026 | Project end: 01.06.2026

---

## Phase 1 — Analysis & Requirements

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-01 | Requirements & Domain Modeling | Define building/unit/sensor hierarchy, incident types, RBAC actors, user stories, acceptance criteria | — | 2 | Analyst | 01.04 | 02.04 |
| T-02 | System Architecture Design | Choose service split (crud/workers/shared/crudx), messaging topology (Kafka topics), DI strategy (Dishka), ORM approach | — | 2 | BE Dev | 01.04 | 02.04 |

---

## Phase 2 — Design & Architecture

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-03 | API Contract Design | Define all REST endpoints, request/response schemas, HTTP status codes, permission matrix | T-01, T-02 | 1 | BE Dev | 03.04 | 03.04 |
| T-04 | Database Schema Design | ERD for 9 tables (buildings, units, sensors, metrics, thresholds, energy_balances, average_loads, peak_loads, incidents + users), FK rules, cascade strategy | T-01, T-02 | 2 | DevOps | 03.04 | 04.04 |
| T-05 | Dev Environment & Docker Base | Docker Compose skeleton, PostgreSQL + Kafka containers, health-checks, env-var layout | T-02 | 1 | DevOps | 03.04 | 03.04 |
| T-06 | Frontend Wireframes | Low-fidelity wireframes for DashboardView, BuildingTabs, SensorsView, UsageChart, ThresholdsView, Auth pages | T-01 | 2 | FE Dev | 03.04 | 04.04 |

---

## Phase 3 — Development

### Shared Kernel & DB

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-07 | Shared Kernel Package | `greenops-shared` package: enums (BuildingType, SensorType, ThresholdType, TariffZone, IncidentType…), base exceptions, dataclass entities, DTOs | T-03, T-04 | 2 | BE Dev | 07.04 | 08.04 |
| T-08 | SQLAlchemy ORM Models | Mapped `*Model` classes for all 9 tables + `users`, `DeclarativeBase`, `__init__` re-exports for Alembic auto-detect | T-04, T-07 | 1 | DevOps | 09.04 | 09.04 |
| T-09 | Alembic Migrations | `alembic.ini`, `env.py`, 4 versioned scripts: initial tables, cascade delete, users table, role column | T-08 | 1 | DevOps | 10.04 | 10.04 |

### crudx Library

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-10 | crudx Library | `AsyncSqlAlchemyGateway` (select/insert/update/delete), `SqlalchemyConfig[CreateDTO,Entity,Model]`, CRUD decorators, `AsyncTransactionsDatabaseGateway`, error mapping (IntegrityError → EntityAlreadyExistsException) | T-07 | 3 | BE Dev | 09.04 | 11.04 |

### CRUD Backend Service

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-11 | CRUD Domain Layer | Abstract repository ABCs for Building, Unit, Sensor, Threshold, Metric, EnergyBalance, AverageLoad + domain exceptions per aggregate | T-07 | 1 | BE Dev | 09.04 | 09.04 |
| T-12 | Auth System (JWT + bcrypt) | `JwtTokensGateway` (HS256, access 1h/refresh 30d), `BcryptSecurityGateway` (salt + hash), `TokensGateway` & `SecurityGateway` ABCs, `AuthenticateUseCase`, `AuthorizeUseCase`, `LoginUseCase`, `RegisterUseCase` | T-11 | 2 | BE Dev | 10.04 | 11.04 |
| T-13 | CRUD Application Layer | `BuildingService`, `UnitService`, `SensorService` (XOR attachment validation), `ThresholdService`, `EnergyBalanceService.run_daily()`, `AverageLoadService.run_hourly()`, `PermissionsEnum`, `ROLE_PERMISSIONS` role map | T-11, T-12 | 3 | BE Dev | 14.04 | 16.04 |
| T-14 | CRUD DB Repositories | Concrete SQLAlchemy implementations for all repositories using crudx decorators + Adaptix mappers for each aggregate | T-10, T-11, T-09 | 2 | DevOps | 14.04 | 15.04 |
| T-15 | CRUD API Layer | FastAPI routers for `/auth`, `/buildings`, `/units`, `/sensors`, `/thresholds`, `/energy-balances`; Pydantic schemas; `get_current_user` / `require_permission` dependencies; exception handlers | T-13, T-14 | 3 | BE Dev | 17.04 | 21.04 |
| T-16 | Dishka DI Container | All 5 providers (Config, Database, Repositories, Services, Auth), `create_container()`, scope wiring (Application/Request), `setup_dishka(container, app)` | T-15 | 1 | BE Dev | 22.04 | 22.04 |
| T-17 | APScheduler Jobs | `register_jobs()`: `run_average_load` (`:05` past each hour), `run_energy_balance` (`00:10` daily); container integration; scheduler startup/shutdown lifecycle | T-13, T-16 | 1 | BE Dev | 23.04 | 23.04 |

### Workers Service

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-18 | Workers Service Setup | FastStream app factory, `KafkaBroker`, `KafkaRouter`, `setup_dishka`, workers `Config` dataclass, engine/session setup | T-05, T-07 | 1 | BE Dev | 09.04 | 09.04 |
| T-19 | TelemetryService + SpikeDetector | `TelemetryService.process()`: persist `Metric`, call `SpikeDetector`; `SpikeDetector`: UPPER/LOWER threshold comparison, severity logic (HIGH if value > limit×1.5); atomic `PeakLoad + Incident` creation; publish `IncidentCreatedEvent` | T-18, T-10, T-09 | 2 | BE Dev | 14.04 | 15.04 |
| T-20 | Kafka Consumers & Simulator | `on_telemetry_raw` and `on_incident_created` subscriber handlers; `simulator.py` (modes: default/normal/spike, CLI args: sensor-id, rate, threshold, bootstrap-servers) | T-18 | 1 | BE Dev | 16.04 | 16.04 |

### Frontend

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-21 | Vue 3 + Vite Setup | Project scaffold, Vue Router, Chart.js, Axios install, folder structure (api/, components/, composables/, views/) | T-06 | 1 | FE Dev | 07.04 | 07.04 |
| T-22 | API Client Layer | Axios base instance, typed wrappers for all CRUD endpoints + auth; composables: `useAuth`, `useBuildings`, `useSensors`, `useMetrics` | T-21, T-03 | 1 | FE Dev | 08.04 | 08.04 |
| T-23 | Auth Views | `LoginView`, `RegisterView`; token storage; route guards; error display | T-22 | 2 | FE Dev | 09.04 | 10.04 |
| T-24 | DashboardView + StatsCards | Building list, `StatsCards` summary widgets, incident badge markers, navigation to BuildingTabs | T-22, T-23 | 3 | FE Dev | 11.04 | 15.04 |
| T-25 | BuildingTabs + SensorsView | Tab navigation per building, sensor list table, sensor type display, threshold status indicators | T-24 | 2 | FE Dev | 16.04 | 17.04 |
| T-26 | UsageChart (Chart.js) | Energy balance line chart, date-range picker, building selector, empty state, data fetching from `/energy-balances` | T-25 | 2 | FE Dev | 18.04 | 21.04 |
| T-27 | ThresholdsView | Threshold table, create/edit modal, `PUT /thresholds/{id}`, validation, inline error display | T-26 | 1 | FE Dev | 22.04 | 22.04 |

### DevOps / Infrastructure

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-28 | Nginx Configuration | `nginx.conf`: proxy `/api/*` → `crud:8000`, `/` → `frontend:3000`, gzip, upstream health | T-05 | 1 | DevOps | 04.04 | 04.04 |
| T-29 | Full Docker Compose Stack | All 11 services: postgres, kafka, migrations (one-shot), crud, workers, frontend, gateway, prometheus, grafana, cadvisor, postgres-exporter, kafka-exporter; health-check dependencies | T-05, T-28, T-04 | 2 | DevOps | 07.04 | 08.04 |
| T-30 | Prometheus + Grafana Setup | `prometheus.yml` scrape config, Grafana datasource, cAdvisor + DB/Kafka exporters, `/metrics` endpoint on crud | T-29 | 2 | DevOps | 09.04 | 10.04 |

---

## Phase 4 — Testing & QA

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-31 | Unit Tests | crudx gateway tests (conftest, create/read/update/delete); `SpikeDetector` unit tests; `SensorService` XOR validation tests; mocked repository tests | T-10, T-19, T-13 | 2 | QA | 17.04 | 18.04 |
| T-32 | Integration Testing | API endpoint tests (auth flow, CRUD round-trips, permission checks); DB transaction tests; workers Kafka consumer smoke tests against running stack | T-15, T-16, T-17, T-31 | 2 | QA | 24.04 | 25.04 |
| T-33 | E2E Testing with Simulator | Full pipeline: simulator → Kafka → workers → PostgreSQL → API → frontend; incident creation verification; energy balance trigger | T-32, T-30, T-27, T-20 | 2 | QA | 28.04 | 29.04 |

---

## Phase 5 — Deployment & Documentation

| Task ID | Task Name | Description | Dependencies | Est. (days) | Role | Start | End |
|---|---|---|---|---|---|---|---|
| T-34 | Technical Documentation | API reference, setup guide, architecture overview, configuration reference | T-15 | 2 | Analyst | 22.04 | 23.04 |
| T-35 | Bug Fixes Buffer | Fix issues found in T-33; regression checks | T-33 | 1 | BE+FE | 30.04 | 30.04 |
| T-36 | Final Deployment & Smoke Tests | `docker compose up --build` on clean env; verify all containers healthy; confirm migrations; run simulator check | T-35, T-34 | 1 | DevOps | 30.04 | 30.04 |
