# GreenOps — Presentation Talking Points

> Speaker notes for a project planning walkthrough.  
> Audience: technical team + stakeholders.

---

## What the Project Does

- GreenOps is a smart-city energy monitoring platform: it ingests real-time sensor telemetry via Kafka, detects anomalies (overloads and leaks), computes daily energy loss per building, and surfaces everything through a Vue 3 dashboard — backed by a FastAPI microservices architecture
- The core value is identifying "commercial losses" — the gap between what a building-level meter reads and the sum of individual apartment meters — and doing it automatically, 24/7, without manual intervention

---

## Phases Identified

| Phase | Days | Summary |
|---|---|---|
| 1 — Analysis | 1–2 | Domain modeling and architecture decisions |
| 2 — Design | 3–5 | Schema, API contracts, wireframes, Docker skeleton |
| 3 — Development | 5–17 | Four parallel streams: backend, frontend, workers, DevOps |
| 4 — Testing | 13–19 | Unit → integration (E2E falls past deadline) |
| 5 — Docs & Deploy | 16–19+ | Documentation runs in parallel; deployment is post-deadline |

- **Phase 1–2 are deliberately short** — the domain model is well-defined and the team is small; long planning phases would burn runway
- **Phase 3 is where 80% of risk lives** — it is the longest phase with the most sequential dependencies
- **Phase 4 starts before Phase 3 ends** — unit tests begin on day 13 while API development is still in progress

---

## Gantt Walk-Through

- **Days 1–2:** Everyone is in planning mode — analysts and architect work in parallel; no code written yet
- **Days 3–4:** The team fans out: DB engineer owns schema, DevOps starts Docker, frontend begins wireframes, BE writes API contracts
- **Days 5–9 (the critical foundation sprint):** Shared kernel, crudx library, domain layer, and auth are all built here; most later tasks are blocked on these completing; this is the highest-risk week
- **Days 10–16 (the build sprint):** All four streams run in full parallel — this is the busiest and most productive stretch; the Gantt is widest here
- **Days 17–19:** Integration and unit testing compress into the final days of the sprint; documentation runs in parallel; E2E testing, bug fixes, and deployment follow in days 20–22

**Key parallel observations:**
- The frontend stream (FE Dev) runs completely independent of the backend after day 8 — the API client is already typed from the contracts
- The DevOps stream (Docker, Nginx, Prometheus) has 9–13 days of float — it will never be on the critical path
- The backend developer is fully serialized from day 7 to day 17 — one task must finish before the next starts; no parallelization is possible

---

## PERT Walk-Through

- Each PERT node carries three time estimates: optimistic, most likely, pessimistic. The expected time is the weighted average: `(min + 4×likely + max) / 6`
- **High-variance tasks** (σ² = 0.25) are where estimates are least reliable:
  - T-10 crudx library (custom internal library, novel design)
  - T-12 auth system (security logic tends to expand in scope)
  - T-13 CRUD application layer (6 services + permission matrix + calculators)
  - T-15 CRUD API layer (most lines of infrastructure code in the project)
  - T-24 DashboardView (complex stateful Vue component)
  - T-31 integration testing (outcome depends on bug density)
- **Low-variance tasks** (σ² ≤ 0.063) are reliable and quick: migrations, domain layer, scheduler jobs, Nginx, simulator
- The PERT expected duration on the critical path is **20.25 days** against a 19-day deadline — a shortfall of 1.25 days

---

## Critical Path Explanation

```
T-01/T-02 → T-04 → T-07 → T-11 → T-12 → T-13 → T-15 → T-16 → T-17 → T-32
```

- The critical path runs entirely through **backend development** — not frontend, not DevOps
- It represents the minimum sequence that cannot be shortened without either splitting tasks across more developers or cutting scope
- **Any single-day slip on T-13 (CRUD application layer) or T-15 (API layer) directly pushes the final delivery date**
- T-07 (shared kernel) is the earliest "merge point" — it is where all streams converge and where a 1-day delay ripples to every downstream task simultaneously
- The PERT probability calculation shows only **~15% chance** of completing the critical path within the exact 19-day nominal window — realistic estimates push expected completion to 20.25 days

---

## Key Risks and Bottlenecks

### 🚨 Critical Risks

1. **Single-person bottleneck on the entire critical path**
   - Ten of nineteen critical-path tasks are assigned to one backend developer
   - Illness, context switching, or any underestimate on T-13 or T-15 cascades immediately
   - Mitigation: assign the DevOps engineer to T-14 (CRUD DB repositories) starting April 14 to parallelize that week

### ⚠️ Moderate Risks

2. **crudx library has only 1 day of float**
   - It is a custom internal library — not an off-the-shelf dependency
   - If implementation takes 4 days instead of 3, it joins the critical path
   - Mitigation: simplify the initial scope (fewer decorator variants, no transaction mixin until needed)

3. **T-13 (CRUD application layer) — largest single task, most dependencies**
   - 3 days estimated, 5 days maximum — this is the task most likely to slip
   - It produces 6 services + permission system + two calculator jobs
   - If it takes 4 days, T-15 (API layer) starts one day late and integration testing moves to April 28 — past the deadline

4. **Auth security complexity (T-12)**
   - JWT + bcrypt + RBAC permission provider is 2 days estimated
   - Auth systems routinely expand: refresh token rotation, edge cases in permission inheritance, activation flow
   - Mitigation: freeze scope to exactly what's in the codebase — no refresh endpoint, no activation email in this sprint

5. **Weekend spans on critical tasks**
   - T-15 (API layer) runs Apr 17–18 then Apr 21 — a Friday slip costs 2 calendar days
   - T-26 (UsageChart) has the same exposure
   - Mitigation: schedule code reviews for Wednesday/Thursday to catch blockers before the weekend

### ℹ️ Low Risks (Informational)

6. **Frontend has 3 days of float — but it is not "free"**
   - All 3 days will be consumed if T-15 (API layer) delivers late and FE cannot finalize integration
   - The frontend developer should use the float to build against mocked data and switch to live data when T-15 lands

7. **No dedicated bug-fix window in the main sprint**
   - T-35 (bug fixes) follows E2E testing in the final project days
   - If integration testing (T-32) finds critical bugs, there is no time to fix them before E2E begins
   - Mitigation: run a lightweight smoke test after T-17 to surface bugs one day early

---

## Recommended Mitigations Summary

| Risk | Action | Owner | By |
|---|---|---|---|
| BE bottleneck | Assign DevOps to T-14 (DB repos) | BE + DevOps | Apr 14 |
| crudx scope creep | Lock crudx API surface before T-10 starts | BE | Apr 8 |
| T-13 overrun | Daily check-in on service progress | PM | Apr 14–16 |
| Weekend slippage | Code review checkpoint every Thursday | Team | Weekly |
| Late bug discovery | Smoke test after T-17 (Apr 23) | QA | Apr 23 |
