# GreenOps — Декомпозиция технических задач

> Предполагаемая команда: Backend-разработчик (BE), Frontend-разработчик (FE), DB/DevOps-инженер (DevOps), QA/Аналитик (QA).  
> Backend-разработчик совмещает роль архитектора в фазах 1–2.  
> Начало проекта: 01.04.2026 | Завершение проекта: 01.06.2026

---

## Фаза 1 — Анализ и требования

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-01 | Сбор требований и моделирование домена | Определить иерархию здание/юнит/датчик, типы инцидентов, акторы RBAC, пользовательские истории, критерии приёмки | — | 2 | Аналитик | 01.04 | 02.04 |
| T-02 | Проектирование системной архитектуры | Выбрать разбивку на сервисы (crud/workers/shared/crudx), топологию сообщений (Kafka-топики), стратегию DI (Dishka), подход ORM | — | 2 | BE Dev | 01.04 | 02.04 |

---

## Фаза 2 — Дизайн и архитектура

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-03 | Проектирование API-контракта | Определить все REST-эндпоинты, схемы запросов/ответов, HTTP-коды статусов, матрицу разрешений | T-01, T-02 | 1 | BE Dev | 03.04 | 03.04 |
| T-04 | Проектирование схемы БД | ERD для 9 таблиц (buildings, units, sensors, metrics, thresholds, energy_balances, average_loads, peak_loads, incidents + users), правила FK, стратегия каскадного удаления | T-01, T-02 | 2 | DevOps | 03.04 | 04.04 |
| T-05 | Среда разработки и базовый Docker | Скелет Docker Compose, контейнеры PostgreSQL + Kafka, health-check'и, структура переменных окружения | T-02 | 1 | DevOps | 03.04 | 03.04 |
| T-06 | Макеты интерфейса (Wireframes) | Низкодетальные макеты для DashboardView, BuildingTabs, SensorsView, UsageChart, ThresholdsView, страниц авторизации | T-01 | 2 | FE Dev | 03.04 | 04.04 |

---

## Фаза 3 — Разработка

### Shared Kernel и БД

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-07 | Пакет Shared Kernel | Пакет `greenops-shared`: перечисления (BuildingType, SensorType, ThresholdType, TariffZone, IncidentType…), базовые исключения, dataclass-сущности, DTO | T-03, T-04 | 2 | BE Dev | 07.04 | 08.04 |
| T-08 | ORM-модели SQLAlchemy | Mapped-классы `*Model` для всех 9 таблиц + `users`, `DeclarativeBase`, реэкспорт в `__init__` для автодетектирования Alembic | T-04, T-07 | 1 | DevOps | 09.04 | 09.04 |
| T-09 | Миграции Alembic | `alembic.ini`, `env.py`, 4 версионированных скрипта: начальные таблицы, каскадное удаление, таблица пользователей, колонка роли | T-08 | 1 | DevOps | 10.04 | 10.04 |

### Библиотека crudx

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-10 | Библиотека crudx | `AsyncSqlAlchemyGateway` (select/insert/update/delete), `SqlalchemyConfig[CreateDTO,Entity,Model]`, CRUD-декораторы, `AsyncTransactionsDatabaseGateway`, маппинг ошибок (IntegrityError → EntityAlreadyExistsException) | T-07 | 3 | BE Dev | 09.04 | 11.04 |

### CRUD Backend-сервис

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-11 | Доменный слой CRUD | Абстрактные ABC-репозитории для Building, Unit, Sensor, Threshold, Metric, EnergyBalance, AverageLoad + доменные исключения на каждый агрегат | T-07 | 1 | BE Dev | 09.04 | 09.04 |
| T-12 | Система аутентификации (JWT + bcrypt) | `JwtTokensGateway` (HS256, access 1ч/refresh 30д), `BcryptSecurityGateway` (соль + хэш), ABC-интерфейсы `TokensGateway` и `SecurityGateway`, `AuthenticateUseCase`, `AuthorizeUseCase`, `LoginUseCase`, `RegisterUseCase` | T-11 | 2 | BE Dev | 10.04 | 11.04 |
| T-13 | Прикладной слой CRUD | `BuildingService`, `UnitService`, `SensorService` (XOR-валидация привязки), `ThresholdService`, `EnergyBalanceService.run_daily()`, `AverageLoadService.run_hourly()`, `PermissionsEnum`, карта ролей `ROLE_PERMISSIONS` | T-11, T-12 | 3 | BE Dev | 14.04 | 16.04 |
| T-14 | DB-репозитории CRUD | Конкретные реализации репозиториев на SQLAlchemy с crudx-декораторами + Adaptix-маппер для каждого агрегата | T-10, T-11, T-09 | 2 | DevOps | 14.04 | 15.04 |
| T-15 | API-слой CRUD | FastAPI-роутеры для `/auth`, `/buildings`, `/units`, `/sensors`, `/thresholds`, `/energy-balances`; Pydantic-схемы; зависимости `get_current_user` / `require_permission`; обработчики исключений | T-13, T-14 | 3 | BE Dev | 17.04 | 21.04 |
| T-16 | DI-контейнер Dishka | Все 5 провайдеров (Config, Database, Repositories, Services, Auth), `create_container()`, привязка скоупов (Application/Request), `setup_dishka(container, app)` | T-15 | 1 | BE Dev | 22.04 | 22.04 |
| T-17 | Задачи APScheduler | `register_jobs()`: `run_average_load` (в `:05` каждого часа), `run_energy_balance` (`00:10` ежедневно); интеграция с контейнером; жизненный цикл планировщика | T-13, T-16 | 1 | BE Dev | 23.04 | 23.04 |

### Workers-сервис

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-18 | Настройка Workers-сервиса | Фабрика приложения FastStream, `KafkaBroker`, `KafkaRouter`, `setup_dishka`, датакласс `Config` для воркеров, инициализация движка и сессии | T-05, T-07 | 1 | BE Dev | 09.04 | 09.04 |
| T-19 | TelemetryService + SpikeDetector | `TelemetryService.process()`: сохранение `Metric`, вызов `SpikeDetector`; `SpikeDetector`: сравнение с UPPER/LOWER-порогами, логика severity (HIGH если значение > лимит×1.5); атомарное создание `PeakLoad + Incident`; публикация `IncidentCreatedEvent` | T-18, T-10, T-09 | 2 | BE Dev | 14.04 | 15.04 |
| T-20 | Kafka-потребители и симулятор | Обработчики `on_telemetry_raw` и `on_incident_created`; `simulator.py` (режимы: default/normal/spike, аргументы CLI: sensor-id, rate, threshold, bootstrap-servers) | T-18 | 1 | BE Dev | 16.04 | 16.04 |

### Frontend

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-21 | Настройка Vue 3 + Vite | Скаффолдинг проекта, Vue Router, Chart.js, установка Axios, структура директорий (api/, components/, composables/, views/) | T-06 | 1 | FE Dev | 07.04 | 07.04 |
| T-22 | API-клиентский слой | Базовый инстанс Axios, типизированные обёртки для всех CRUD-эндпоинтов + auth; composables: `useAuth`, `useBuildings`, `useSensors`, `useMetrics` | T-21, T-03 | 1 | FE Dev | 08.04 | 08.04 |
| T-23 | Представления авторизации | `LoginView`, `RegisterView`; хранение токена; маршрутные охранники; отображение ошибок | T-22 | 2 | FE Dev | 09.04 | 10.04 |
| T-24 | DashboardView + StatsCards | Список зданий, виджеты сводной статистики `StatsCards`, маркеры инцидентов, навигация к BuildingTabs | T-22, T-23 | 3 | FE Dev | 11.04 | 15.04 |
| T-25 | BuildingTabs + SensorsView | Вкладки навигации по зданию, таблица датчиков, отображение типа датчика, индикаторы статуса порогов | T-24 | 2 | FE Dev | 16.04 | 17.04 |
| T-26 | UsageChart (Chart.js) | Линейный график энергетического баланса, выбор периода, выбор здания, пустое состояние, загрузка данных из `/energy-balances` | T-25 | 2 | FE Dev | 18.04 | 21.04 |
| T-27 | ThresholdsView | Таблица порогов, модальное окно создания/редактирования, `PUT /thresholds/{id}`, валидация, отображение ошибок | T-26 | 1 | FE Dev | 22.04 | 22.04 |

### DevOps / Инфраструктура

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-28 | Настройка Nginx | `nginx.conf`: проксирование `/api/*` → `crud:8000`, `/` → `frontend:3000`, gzip, upstream health | T-05 | 1 | DevOps | 04.04 | 04.04 |
| T-29 | Полный Docker Compose-стек | Все 11 сервисов: postgres, kafka, migrations (одноразовый), crud, workers, frontend, gateway, prometheus, grafana, cadvisor, postgres-exporter, kafka-exporter; зависимости health-check | T-05, T-28, T-04 | 2 | DevOps | 07.04 | 08.04 |
| T-30 | Настройка Prometheus + Grafana | Конфиг `prometheus.yml`, источник данных Grafana, экспортеры cAdvisor + DB/Kafka, эндпоинт `/metrics` в crud-сервисе | T-29 | 2 | DevOps | 09.04 | 10.04 |

---

## Фаза 4 — Тестирование и QA

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-31 | Юнит-тесты | Тесты шлюза crudx (conftest, create/read/update/delete); юнит-тесты `SpikeDetector`; тесты XOR-валидации `SensorService`; тесты с мокированными репозиториями | T-10, T-19, T-13 | 2 | QA | 17.04 | 18.04 |
| T-32 | Интеграционное тестирование | Тесты API-эндпоинтов (поток авторизации, CRUD-циклы, проверка разрешений); тесты транзакций БД; дымовые тесты Kafka-потребителей воркеров на запущенном стеке | T-15, T-16, T-17, T-31 | 2 | QA | 24.04 | 25.04 |
| T-33 | E2E-тестирование с симулятором | Полный пайплайн: симулятор → Kafka → workers → PostgreSQL → API → frontend; верификация создания инцидентов; триггер энергетического баланса | T-32, T-30, T-27, T-20 | 2 | QA | 28.04 | 29.04 |

---

## Фаза 5 — Деплой и документация

| ID задачи | Название | Описание | Зависимости | Оценка (дни) | Роль | Начало | Конец |
|---|---|---|---|---|---|---|---|
| T-34 | Техническая документация | Справочник API, руководство по установке, обзор архитектуры, справочник конфигурации | T-15 | 2 | Аналитик | 22.04 | 23.04 |
| T-35 | Буфер на исправление ошибок | Исправление проблем, обнаруженных в T-33; регрессионные проверки | T-33 | 1 | BE+FE | 30.04 | 30.04 |
| T-36 | Финальный деплой и дымовые тесты | `docker compose up --build` в чистом окружении; проверка работоспособности всех контейнеров; подтверждение миграций; запуск симулятора | T-35, T-34 | 1 | DevOps | 30.04 | 30.04 |
