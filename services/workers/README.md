# workers — Data Plane Service

FastStream (Kafka) consumer service. Ingests raw telemetry, detects spikes, creates incidents, and publishes events. No REST API.

## Responsibilities

- Consume `telemetry.raw` → persist `Metric` → run `SpikeDetector` → if spike detected: create `PeakLoad` + `Incident` in one DB transaction, then publish `IncidentCreatedEvent` to `incidents.created`
- Consume `incidents.created` → log/audit (extensible hook for future integrations)

## Kafka topics

| Topic | Direction | Handler |
|-------|-----------|---------|
| `telemetry.raw` | inbound | `TelemetryService.process()` |
| `incidents.created` | inbound | audit logger |
| `incidents.created` | outbound | published by `TelemetryService` on spike |

Message payload is a plain JSON dict serialised/deserialised via Adaptix `Retort`.

## Spike detection logic

`SpikeDetector` is a pure, stateless class — no I/O, no async:

| Condition | Incident type |
|-----------|--------------|
| `value > threshold.limit_value` (UPPER threshold) | `OVERLOAD` |
| `value < threshold.limit_value` (LOWER threshold) | `LEAK` |
| `value ≈ 0` for `duration_seconds > 600` | `IDLE` |

Severity is `HIGH` when `value > limit_value * 1.5`, otherwise `LOW`.

> **MVP trade-off:** `duration_seconds` is always `0` — idle detection requires stateful windowing, deferred post-MVP.

## Stack

| Layer | Technology |
|-------|-----------|
| Messaging | FastStream + aiokafka |
| DI | Dishka (`setup_dishka` for FastStream) |
| ORM | SQLAlchemy 2.0 |
| DB driver | asyncpg |
| CRUD helpers | crudx |
| DTO mapping | Adaptix |

## Architecture

```
src/
├── domain/
│   ├── spike_detector.py      # Pure detection logic, no dependencies
│   └── */repository.py        # ABCs for all repositories
├── application/
│   └── telemetry/service.py   # Orchestrates: persist → detect → publish
└── infrastructure/
    ├── db/                    # crudx repositories (metric, incident, peak_load)
    │   ├── threshold/         # Raw SQLAlchemy read (read-only, no crudx needed)
    │   └── average_load/      # Raw SQLAlchemy read
    ├── kafka/
    │   ├── telemetry_consumer.py
    │   ├── incident_consumer.py
    │   ├── publisher.py       # KafkaEventPublisher implements EventPublisher protocol
    │   └── app.py             # FastStream app factory
    ├── configs/               # Config dataclass
    └── providers/             # Dishka providers; KafkaBroker injected via context
```

The `EventPublisher` is a `Protocol` — `TelemetryService` has no import of FastStream, keeping domain/application layers framework-free.

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address, e.g. `kafka:9092` |

## Running locally

```bash
cd services/workers
poetry install
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/greenops_db \
  KAFKA_BOOTSTRAP_SERVERS=localhost:9092 \
  PYTHONPATH=src poetry run python main.py
```

## Running tests

```bash
cd services/workers
poetry run python -m pytest src/tests/
```
