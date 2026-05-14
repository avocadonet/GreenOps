# GreenOps — PERT Diagram

> PERT formula: **te = (min + 4 × likely + max) / 6**  
> Variance: **σ² = ((max − min) / 6)²**  
> Day numbers map to working days starting Apr 1, 2026.

---

## PERT Nodes

| Task ID | Task Name | Min (d) | Likely (d) | Max (d) | te (d) | σ² |
|---|---|---|---|---|---|---|
| T-01 | Requirements & Domain Modeling | 1 | 2 | 3 | **2.00** | 0.11 |
| T-02 | System Architecture Design | 1 | 2 | 4 | **2.17** | 0.25 |
| T-03 | API Contract Design | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-04 | Database Schema Design | 1 | 2 | 3 | **2.00** | 0.11 |
| T-05 | Dev Environment & Docker Base | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-06 | Frontend Wireframes | 1 | 2 | 3 | **2.00** | 0.11 |
| T-07 | Shared Kernel Package | 1 | 2 | 4 | **2.17** | 0.25 |
| T-08 | SQLAlchemy ORM Models | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-09 | Alembic Migrations | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-10 | crudx Library | 2 | 3 | 5 | **3.17** | 0.25 |
| T-11 | CRUD Domain Layer | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-12 | Auth System (JWT + bcrypt) | 1 | 2 | 4 | **2.17** | 0.25 |
| T-13 | CRUD Application Layer | 2 | 3 | 5 | **3.17** | 0.25 |
| T-14 | CRUD DB Repositories | 1 | 2 | 3 | **2.00** | 0.11 |
| T-15 | CRUD API Layer | 2 | 3 | 5 | **3.17** | 0.25 |
| T-16 | Dishka DI Container | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-17 | APScheduler Jobs | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-18 | Workers Service Setup | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-19 | TelemetryService + SpikeDetector | 1 | 2 | 3 | **2.00** | 0.11 |
| T-20 | Kafka Consumers & Simulator | 0.5 | 1 | 1.5 | **1.00** | 0.028 |
| T-21 | Vue 3 + Vite Setup | 0.5 | 1 | 1.5 | **1.00** | 0.028 |
| T-22 | API Client Layer | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-23 | Auth Views | 1 | 2 | 3 | **2.00** | 0.11 |
| T-24 | DashboardView + StatsCards | 2 | 3 | 5 | **3.17** | 0.25 |
| T-25 | BuildingTabs + SensorsView | 1 | 2 | 3 | **2.00** | 0.11 |
| T-26 | UsageChart (Chart.js) | 1 | 2 | 4 | **2.17** | 0.25 |
| T-27 | ThresholdsView | 0.5 | 1 | 2 | **1.08** | 0.063 |
| T-28 | Nginx Configuration | 0.5 | 1 | 1.5 | **1.00** | 0.028 |
| T-29 | Full Docker Compose Stack | 1 | 2 | 3 | **2.00** | 0.11 |
| T-30 | Prometheus + Grafana Setup | 1 | 2 | 3 | **2.00** | 0.11 |
| T-31 | Unit Tests | 1 | 2 | 4 | **2.17** | 0.25 |
| T-32 | Integration Testing | 2 | 2 | 4 | **2.33** | 0.11 |
| T-33 | E2E Testing with Simulator | 1 | 2 | 4 | **2.17** | 0.25 |
| T-34 | Technical Documentation | 1 | 2 | 3 | **2.00** | 0.11 |
| T-35 | Bug Fixes Buffer | 1 | 1 | 3 | **1.33** | 0.11 |
| T-36 | Final Deployment & Smoke Tests | 0.5 | 1 | 2 | **1.08** | 0.063 |

---

## PERT Connections

```
START  → T-01   project begins
START  → T-02   project begins (parallel)

T-01   → T-03   requirements complete
T-02   → T-03   architecture decided
T-01   → T-04   requirements complete
T-02   → T-04   architecture decided
T-02   → T-05   technology stack confirmed
T-01   → T-06   user stories ready for wireframes

T-03   → T-07   API contracts define entity shape
T-04   → T-07   DB schema defines entities
T-04   → T-08   schema ready for ORM mapping
T-07   → T-08   shared entities defined
T-08   → T-09   models ready for migration generation
T-07   → T-10   shared entities / DTOs available
T-07   → T-11   domain entities defined
T-05   → T-18   Docker infra available
T-07   → T-18   shared kernel available
T-05   → T-28   Docker base for Nginx
T-05   → T-29   base infrastructure ready
T-04   → T-29   DB config confirmed
T-28   → T-29   Nginx config for gateway
T-29   → T-30   running stack to scrape
T-06   → T-21   wireframes guide implementation

T-09   → T-14   migrations define schema contracts
T-10   → T-14   crudx gateway available
T-11   → T-14   domain repos defined
T-11   → T-12   user entity defined
T-11   → T-13   all domain repos defined
T-12   → T-13   auth use cases ready
T-13   → T-15   services ready for HTTP wiring
T-14   → T-15   DB repos available for DI
T-18   → T-19   workers infra ready
T-10   → T-19   crudx for workers DB access
T-09   → T-19   migrations applied
T-18   → T-20   Kafka topics established
T-15   → T-16   all routers / providers to wire
T-13   → T-17   services to schedule
T-16   → T-17   container available for scheduler

T-21   → T-22   Vue project bootstrapped
T-03   → T-22   API contract for typed client
T-22   → T-23   API client for auth calls
T-22   → T-24   API client for data
T-23   → T-24   auth guards for dashboard
T-24   → T-25   building context established
T-25   → T-26   sensor / building tabs for chart
T-26   → T-27   threshold data context available

T-10   → T-31   crudx unit tests
T-19   → T-31   SpikeDetector tests
T-13   → T-31   SensorService XOR tests
T-15   → T-32   API endpoints ready
T-16   → T-32   DI container ready
T-17   → T-32   scheduler registered
T-31   → T-32   unit tests passed

T-32   → T-33   integration tests passed
T-30   → T-33   monitoring stack available
T-27   → T-33   full UI available
T-20   → T-33   simulator available
T-15   → T-34   API reference finalized

T-33   → T-35   bugs identified
T-35   → T-36   fixes applied
T-34   → T-36   docs complete

T-36   → END    full project end
```

---

## draw.io Node Format

Copy-paste descriptions for building nodes in draw.io.  
Each node: `[TaskID] | Name | te | ES–EF | Float`

```
[T-01] Requirements & Domain Modeling     | te=2.00 | ES=1  EF=2  | Float=0 ★
[T-02] System Architecture Design         | te=2.17 | ES=1  EF=2  | Float=0 ★
[T-03] API Contract Design                | te=1.08 | ES=3  EF=3  | Float=1
[T-04] Database Schema Design             | te=2.00 | ES=3  EF=4  | Float=0 ★
[T-05] Dev Environment & Docker Base      | te=1.08 | ES=3  EF=3  | Float=9
[T-06] Frontend Wireframes                | te=2.00 | ES=3  EF=4  | Float=3
[T-07] Shared Kernel Package              | te=2.17 | ES=5  EF=6  | Float=0 ★
[T-08] SQLAlchemy ORM Models              | te=1.08 | ES=7  EF=7  | Float=2
[T-09] Alembic Migrations                 | te=1.08 | ES=8  EF=8  | Float=2
[T-10] crudx Library                      | te=3.17 | ES=7  EF=9  | Float=1
[T-11] CRUD Domain Layer                  | te=1.08 | ES=7  EF=7  | Float=0 ★
[T-12] Auth System (JWT + bcrypt)         | te=2.17 | ES=8  EF=9  | Float=0 ★
[T-13] CRUD Application Layer             | te=3.17 | ES=10 EF=12 | Float=0 ★
[T-14] CRUD DB Repositories               | te=2.00 | ES=10 EF=11 | Float=1
[T-15] CRUD API Layer                     | te=3.17 | ES=13 EF=15 | Float=0 ★
[T-16] Dishka DI Container                | te=1.08 | ES=16 EF=16 | Float=0 ★
[T-17] APScheduler Jobs                   | te=1.08 | ES=17 EF=17 | Float=0 ★
[T-18] Workers Service Setup              | te=1.08 | ES=7  EF=7  | Float=6
[T-19] TelemetryService + SpikeDetector   | te=2.00 | ES=10 EF=11 | Float=4
[T-20] Kafka Consumers & Simulator        | te=1.00 | ES=8  EF=8  | Float=11
[T-21] Vue 3 + Vite Setup                 | te=1.00 | ES=5  EF=5  | Float=3
[T-22] API Client Layer                   | te=1.08 | ES=6  EF=6  | Float=3
[T-23] Auth Views                         | te=2.00 | ES=7  EF=8  | Float=3
[T-24] DashboardView + StatsCards         | te=3.17 | ES=9  EF=11 | Float=3
[T-25] BuildingTabs + SensorsView         | te=2.00 | ES=12 EF=13 | Float=3
[T-26] UsageChart (Chart.js)              | te=2.17 | ES=14 EF=15 | Float=3
[T-27] ThresholdsView                     | te=1.08 | ES=16 EF=16 | Float=3
[T-28] Nginx Configuration                | te=1.00 | ES=4  EF=4  | Float=13
[T-29] Full Docker Compose Stack          | te=2.00 | ES=5  EF=6  | Float=13
[T-30] Prometheus + Grafana Setup         | te=2.00 | ES=7  EF=8  | Float=11
[T-31] Unit Tests                         | te=2.17 | ES=13 EF=14 | Float=3
[T-32] Integration Testing                | te=2.33 | ES=18 EF=19 | Float=0 ★
[T-33] E2E Testing with Simulator         | te=2.17 | ES=20 EF=21 | Float=0
[T-34] Technical Documentation            | te=2.00 | ES=16 EF=17 | Float=2
[T-35] Bug Fixes Buffer                   | te=1.33 | ES=22 EF=22 | Float=0
[T-36] Final Deployment & Smoke Tests     | te=1.08 | ES=22 EF=22 | Float=0

★ = critical path node
```

---

## Critical Path

```
T-01/T-02 → T-04 → T-07 → T-11 → T-12 → T-13 → T-15 → T-16 → T-17 → T-32
```

### Nominal duration (integer estimates)

```
T-01  2d
T-04  2d   (T-02 also ends day 2, both feed T-04)
T-07  2d
T-11  1d
T-12  2d
T-13  3d
T-15  3d
T-16  1d
T-17  1d
T-32  2d
─────────
Total  19 working days  (Apr 1 – Apr 25, zero buffer)
```

### PERT expected duration on critical path

```
te(T-01) = 2.00
te(T-04) = 2.00
te(T-07) = 2.17
te(T-11) = 1.08
te(T-12) = 2.17
te(T-13) = 3.17
te(T-15) = 3.17
te(T-16) = 1.08
te(T-17) = 1.08
te(T-32) = 2.33
──────────────
Expected duration to T-32 = 20.25 days
Nominal plan to T-32      = 19.00 days
PERT–nominal delta        = +1.25 days
```

### Project variance & probability

```
σ²(critical path) = 0.11 + 0.11 + 0.25 + 0.063 + 0.25 + 0.25 + 0.25 + 0.063 + 0.063 + 0.11
                  = 1.52

σ = √1.52 ≈ 1.23 days

Z = (nominal − expected) / σ
  = (19 − 20.25) / 1.23
  = −1.02

P(complete T-32 within 19-day nominal plan) ≈ 15%
```

> **The critical path to T-32 has only a ~15% probability of completing within the exact 19-day nominal plan.**  
> A 50% probability requires ~20.25 days (+1.25 days of schedule buffer beyond the nominal plan).  
> An 85% probability requires ~21.5 days total (+2.5 days buffer).

---

## Float Summary by Stream

| Stream | Typical Float | Interpretation |
|---|---|---|
| Backend critical path | **0** | Every day matters; no recovery room |
| crudx library (T-10) | 1 | One day slip makes it critical |
| CRUD DB Repositories (T-14) | 1 | Parallel to T-13; barely off critical path |
| Frontend (T-21–T-27) | **3** | Comfortable, but consumed entirely if API is late |
| Workers (T-18–T-20) | 4–11 | Well insulated; independent Kafka stream |
| DevOps / Docker / Nginx | 9–13 | No deadline risk from this stream |
| Monitoring (T-30) | 11 | Lowest priority within deadline |
| Unit Tests (T-31) | 3 | Must start Apr 17; cannot slip |
| Documentation (T-34) | 2 | Can start Apr 22 at latest |
