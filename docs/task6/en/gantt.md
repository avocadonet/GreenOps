# GreenOps — Gantt Chart

> Excel-ready table. Dates: DD.MM.YYYY. Working days only (Mon–Fri).  
> **CRITICAL** = zero float on the critical path.

---

| Task ID | Task Name | Phase | Assignee | Start Date | End Date | Duration (days) | Dependencies | Notes |
|---|---|---|---|---|---|---|---|---|
| T-01 | Requirements & Domain Modeling | 1 – Analysis | Analyst | 01.04.2026 | 02.04.2026 | 2 | — | CRITICAL |
| T-02 | System Architecture Design | 1 – Analysis | BE Dev | 01.04.2026 | 02.04.2026 | 2 | — | CRITICAL; parallel with T-01 |
| T-03 | API Contract Design | 2 – Design | BE Dev | 03.04.2026 | 03.04.2026 | 1 | T-01, T-02 | Float = 1 |
| T-04 | Database Schema Design | 2 – Design | DevOps | 03.04.2026 | 04.04.2026 | 2 | T-01, T-02 | CRITICAL |
| T-05 | Dev Environment & Docker Base | 2 – Design | DevOps | 03.04.2026 | 03.04.2026 | 1 | T-02 | Float = 9 |
| T-06 | Frontend Wireframes | 2 – Design | FE Dev | 03.04.2026 | 04.04.2026 | 2 | T-01 | Float = 3 |
| T-07 | Shared Kernel Package | 3 – Dev / DB | BE Dev | 07.04.2026 | 08.04.2026 | 2 | T-03, T-04 | CRITICAL; blocker for 8 downstream tasks |
| T-08 | SQLAlchemy ORM Models | 3 – Dev / DB | DevOps | 09.04.2026 | 09.04.2026 | 1 | T-04, T-07 | Float = 2 |
| T-09 | Alembic Migrations | 3 – Dev / DB | DevOps | 10.04.2026 | 10.04.2026 | 1 | T-08 | Float = 2 |
| T-10 | crudx Library | 3 – Dev / BE | BE Dev | 09.04.2026 | 11.04.2026 | 3 | T-07 | Float = 1; ⚠️ RISK: underestimated |
| T-11 | CRUD Domain Layer | 3 – Dev / BE | BE Dev | 09.04.2026 | 09.04.2026 | 1 | T-07 | CRITICAL |
| T-18 | Workers Service Setup | 3 – Dev / BE | BE Dev | 09.04.2026 | 09.04.2026 | 1 | T-05, T-07 | Float = 6; parallel with T-11 |
| T-21 | Vue 3 + Vite Setup | 3 – Dev / FE | FE Dev | 07.04.2026 | 07.04.2026 | 1 | T-06 | Float = 3 |
| T-28 | Nginx Configuration | 3 – DevOps | DevOps | 04.04.2026 | 04.04.2026 | 1 | T-05 | Float = 13 |
| T-29 | Full Docker Compose Stack | 3 – DevOps | DevOps | 07.04.2026 | 08.04.2026 | 2 | T-05, T-28, T-04 | Float = 13 |
| T-22 | API Client Layer | 3 – Dev / FE | FE Dev | 08.04.2026 | 08.04.2026 | 1 | T-21, T-03 | Float = 3 |
| T-12 | Auth System (JWT + bcrypt) | 3 – Dev / BE | BE Dev | 10.04.2026 | 11.04.2026 | 2 | T-11 | CRITICAL; ⚠️ RISK: security logic |
| T-30 | Prometheus + Grafana Setup | 3 – DevOps | DevOps | 09.04.2026 | 10.04.2026 | 2 | T-29 | Float = 11 |
| T-23 | Auth Views | 3 – Dev / FE | FE Dev | 09.04.2026 | 10.04.2026 | 2 | T-22 | Float = 3 |
| T-13 | CRUD Application Layer | 3 – Dev / BE | BE Dev | 14.04.2026 | 16.04.2026 | 3 | T-11, T-12 | CRITICAL; ⚠️ RISK: largest single task |
| T-14 | CRUD DB Repositories | 3 – Dev / BE | DevOps | 14.04.2026 | 15.04.2026 | 2 | T-10, T-11, T-09 | Float = 1; parallel with T-13 |
| T-19 | TelemetryService + SpikeDetector | 3 – Dev / BE | BE Dev | 14.04.2026 | 15.04.2026 | 2 | T-18, T-10, T-09 | Float = 4; parallel with T-13 |
| T-24 | DashboardView + StatsCards | 3 – Dev / FE | FE Dev | 11.04.2026 | 15.04.2026 | 3 | T-22, T-23 | Float = 3; spans weekend |
| T-20 | Kafka Consumers & Simulator | 3 – Dev / BE | BE Dev | 16.04.2026 | 16.04.2026 | 1 | T-18 | Float = 11 |
| T-25 | BuildingTabs + SensorsView | 3 – Dev / FE | FE Dev | 16.04.2026 | 17.04.2026 | 2 | T-24 | Float = 3 |
| T-31 | Unit Tests | 4 – Testing | QA | 17.04.2026 | 18.04.2026 | 2 | T-10, T-19, T-13 | Float = 3 |
| T-15 | CRUD API Layer | 3 – Dev / BE | BE Dev | 17.04.2026 | 21.04.2026 | 3 | T-13, T-14 | CRITICAL; spans weekend |
| T-26 | UsageChart (Chart.js) | 3 – Dev / FE | FE Dev | 18.04.2026 | 21.04.2026 | 2 | T-25 | Float = 3; spans weekend |
| T-34 | Technical Documentation | 5 – Docs | Analyst | 22.04.2026 | 23.04.2026 | 2 | T-15 | Float = 2; parallel track |
| T-16 | Dishka DI Container | 3 – Dev / BE | BE Dev | 22.04.2026 | 22.04.2026 | 1 | T-15 | CRITICAL |
| T-27 | ThresholdsView | 3 – Dev / FE | FE Dev | 22.04.2026 | 22.04.2026 | 1 | T-26 | Float = 3 |
| T-17 | APScheduler Jobs | 3 – Dev / BE | BE Dev | 23.04.2026 | 23.04.2026 | 1 | T-13, T-16 | CRITICAL |
| T-32 | Integration Testing | 4 – Testing | QA | 24.04.2026 | 25.04.2026 | 2 | T-15, T-16, T-17, T-31 | CRITICAL; last task within deadline |
| T-33 | E2E Testing with Simulator | 4 – Testing | QA | 28.04.2026 | 29.04.2026 | 2 | T-32, T-30, T-27, T-20 | — |
| T-35 | Bug Fixes Buffer | 5 – Deploy | BE + FE | 30.04.2026 | 30.04.2026 | 1 | T-33 | — |
| T-36 | Final Deployment & Smoke Tests | 5 – Deploy | DevOps | 30.04.2026 | 30.04.2026 | 1 | T-35, T-34 | — |

---

## Visual Timeline (ASCII)

```
WEEK 1  Apr 01–04        WEEK 2  Apr 07–11        WEEK 3  Apr 14–18        WEEK 4  Apr 21–25
Mo Tu We Th Fr           Mo Tu We Th Fr           Mo Tu We Th Fr           Mo Tu We Th Fr
01 02 03 04              07 08 09 10 11           14 15 16 17 18           21 22 23 24 25

── Analyst ──────────────────────────────────────────────────────────────────────────────
T-01[==]                                                                                    Phase 1
                                                 T-31[====]                                 Phase 4
                                                             T-34[====]                     Phase 5

── BE Dev ───────────────────────────────────────────────────────────────────────────────
T-02[==]                                                                                    Phase 1 CRITICAL
         T-03[=]                                                                            Phase 2
               T-07[====]                                                                   Phase 3 CRITICAL
                     T-11[=]                                                                Phase 3 CRITICAL
                     T-12[====]                                                             Phase 3 CRITICAL
                           T-10[======]                                                     Phase 3
                                 T-13[======]                                               Phase 3 CRITICAL
                                 T-19[====]                                                 Phase 3
                                       T-20[=]                                              Phase 3
                                             T-15[======]                                   Phase 3 CRITICAL
                                                       T-16[=]                              Phase 3 CRITICAL
                                                           T-17[=]                          Phase 3 CRITICAL

── FE Dev ───────────────────────────────────────────────────────────────────────────────
T-06[====]                                                                                  Phase 2
               T-21[=]                                                                      Phase 3
                     T-22[=]                                                                Phase 3
                           T-23[====]                                                       Phase 3
                                 T-24[======]                                               Phase 3
                                       T-25[====]                                           Phase 3
                                             T-26[====]                                     Phase 3
                                                       T-27[=]                              Phase 3

── DevOps ───────────────────────────────────────────────────────────────────────────────
T-05[=]                                                                                     Phase 2
T-04[====]                                                                                  Phase 2 CRITICAL
         T-28[=]                                                                            Phase 3
               T-29[====]                                                                   Phase 3
                     T-08[=]                                                                Phase 3
                     T-30[====]                                                             Phase 3
                           T-09[=]                                                          Phase 3
                                 T-14[====]                                                 Phase 3

── QA ───────────────────────────────────────────────────────────────────────────────────
                                             T-31[====]                                     Phase 4
                                                             T-32[====]                     Phase 4 CRITICAL
                                                                        T-33[====]         Phase 4
                                                                                  T-35[=]  Phase 5
                                                                                  T-36[=]  Phase 5
```

---

## Critical Path

```
T-01/T-02 → T-04 → T-07 → T-11 → T-12 → T-13 → T-15 → T-16 → T-17 → T-32
```

Total nominal duration: **19 working days** to T-32; full project completion (T-36) at working day 22
