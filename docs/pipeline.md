# GreenOps — Pipeline описание

Полный путь данных от датчика до дашборда состоит из четырёх этапов.

---

## 1. Приём телеметрии — IoT → Kafka

Данные попадают в систему одним из двух способов:

**Реальное оборудование** (через адаптеры в `services/crud/adapters/`):
- **Tuya**: `TuyaClient` каждые N секунд вызывает `GET /v1.0/devices/{id}/status` Tuya Cloud API. Ответ содержит data-points (`cur_power`, `add_ele`, `cur_voltage`, `cur_current`). `TuyaAdapter` вычисляет дельту kWh между двумя опросами и создаёт `TelemetryMessage`.
- **Xiaomi**: `XiaomiAdapter` опрашивает устройство по miio UDP-протоколу (локально) или через MiCloud API. Нормализует разнородные названия свойств (`power_consumption`, `electric_power`, …) в единый формат.
- **Zigbee2MQTT**: `Zigbee2MqttAdapter` подписывается на MQTT-топики `zigbee2mqtt/<friendly_name>`. Сообщения приходят по событию — при каждом изменении показаний устройства.

Все три адаптера выдают одинаковый объект `TelemetryMessage` → `runner.py` публикует его в Kafka-топик **`telemetry.raw`**.

**Симулятор** (`simulate_all.py`) делает то же самое в обход адаптеров — напрямую публикует JSON в `telemetry.raw`. Используется для разработки и нагрузочного тестирования.

Формат сообщения в топике:
```json
{ "sensor_id": "<uuid>", "value": 1.23, "measurement_unit": "kWh",
  "voltage": 220.1, "current": 0.56, "recorded_at": "2026-05-09T10:00:00Z" }
```

---

## 2. Обработка телеметрии — Workers-сервис

`kafka_consumers.py` содержит два подписчика на FastStream:

**`on_telemetry_raw`** — вызывается на каждое сообщение из `telemetry.raw`:

1. Десериализует JSON → `CreateMetricDTO` через Adaptix `Retort`.
2. Передаёт DTO в `TelemetryService.process()`.

Внутри `process()` всё происходит в одной транзакции:

```
INSERT INTO metrics         ← сохраняем каждое показание безусловно

SELECT threshold            ← читаем настроенный порог для этого датчика
  если порога нет → выходим

SELECT avg_load (latest)    ← читаем базовый уровень (для контекста)

SpikeDetector.detect()      ← чистая функция, никакого I/O
  value > UPPER threshold → SpikeResult(OVERLOAD)
  value < LOWER threshold → SpikeResult(LEAK)
  value ≈ 0 > 600 сек     → SpikeResult(IDLE)
  иначе → None

если spike:
  INSERT INTO peak_loads    ┐  атомарно в одной
  INSERT INTO incidents     ┘  транзакции

COMMIT
```

После коммита (вне транзакции) Workers публикует `IncidentCreatedEvent` в **`incidents.created`**.

**`on_incident_created`** — второй подписчик, читает из `incidents.created`:
- Десериализует событие.
- Пишет строку в stdout-лог (аудит-журнал): тип инцидента, severity, sensor_id, timestamp.
- Коммитит Kafka-offset даже при ошибке десериализации (Poison Pill handling).

---

## 3. Фоновая аналитика — CRUD-сервис, APScheduler

CRUD-сервис запускает два фоновых задания (`infrastructure/scheduler/jobs.py`):

**`average_load_hourly`** — каждый час в :05:
```
AverageLoadService.run_hourly()
  → SELECT AVG(value) FROM metrics WHERE sensor_id=… AND recorded_at > NOW()-1h
  → INSERT INTO average_loads (sensor_id, window_size=HOUR, mean_value, calculated_at)
```
Результат используется Workers как `baseline` при детекции аномалий.

**`energy_balance_daily`** — каждый день в 00:10:
```
EnergyBalanceService.run_daily()
  для каждого здания:
    common_kwh  = SUM(metrics) для COMMON-датчика
    indiv_kwh   = SUM(metrics) для всех INDIVIDUAL-датчиков
    loss_kwh    = common_kwh - indiv_kwh
    loss_percent = loss_kwh / common_kwh × 100
    INSERT INTO energy_balances (building_id, period_start, period_end, loss_kwh, loss_percent)
```
`loss_percent` — это «небаланс» здания: разница между тем, что намерял общедомовой счётчик, и суммой квартирных счётчиков.

---

## 4. API и дашборд — CRUD-сервис + Frontend

CRUD-сервис (FastAPI + Dishka DI) отдаёт данные фронтенду:

| Фронтенд-компонент | Запрос | Откуда данные |
|---|---|---|
| `DashboardView` — карточки зданий | `GET /buildings` | таблица `buildings` |
| `UsageChart` — график потребления | `GET /energy-balances?building_id=…` | таблица `energy_balances` |
| `SensorsView` — список датчиков | `GET /sensors?building_id=…` | таблица `sensors` |
| `ThresholdsView` — пороги | `GET /thresholds?sensor_id=…` | таблица `thresholds` |

Каждый запрос проходит проверку прав через RBAC:
- Глобальная роль на объекте `User.role` (`SUPER_*`)
- Или роль в конкретной организации через `UserOrganizationRole` (`OWNER`, `ADMIN`, `REDACTOR`, `PUBLIC`)

Nginx на порту 80 является единственной точкой входа — он проксирует `/api/*` на CRUD-сервис `:8000` и `/` на Vue 3 SPA `:3000`.

---

## Полная схема

```
IoT датчики / Tuya / Xiaomi / Zigbee2MQTT
           │
           │  adapters/runner.py  (services/crud/adapters/)
           ▼
     Kafka  telemetry.raw
           │
           ▼
     Workers  on_telemetry_raw()
           │
           ├─ INSERT metrics
           ├─ SpikeDetector.detect()
           │        │
           │        └─ spike? ──► INSERT peak_loads + incidents (1 транзакция)
           │                              │
           │                              ▼
           │                    Kafka  incidents.created
           │                              │
           │                              ▼
           │                    Workers  on_incident_created()
           │                              └─ stdout лог (аудит)
           │
     PostgreSQL ◄──────────────────────────────────────────┐
           │                                               │
           │  APScheduler (каждый час / каждый день)       │
           ▼                                               │
     AverageLoadService   EnergyBalanceService             │
           │                      │                        │
           └──────────────────────┘                        │
                    INSERT avg_loads / energy_balances      │
                                                           │
     CRUD-сервис FastAPI  ◄── Nginx :80 ◄── Vue 3 SPA ────┘
           │
           ▼
     Prometheus /metrics  ──►  Grafana  (технический мониторинг)
```
