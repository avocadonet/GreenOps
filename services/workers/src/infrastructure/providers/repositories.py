from dishka import Provider, Scope, provide

from domain.average_load.repository import AverageLoadReadRepository
from domain.incident.repository import IncidentRepository
from domain.metric.repository import MetricRepository
from domain.peak_load.repository import PeakLoadRepository
from domain.threshold.repository import ThresholdReadRepository
from infrastructure.db.average_load.repository import AverageLoadReadDatabaseRepository
from infrastructure.db.incident.repository import IncidentDatabaseRepository
from infrastructure.db.metric.repository import MetricDatabaseRepository
from infrastructure.db.peak_load.repository import PeakLoadDatabaseRepository
from infrastructure.db.threshold.repository import ThresholdReadDatabaseRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    metrics = provide(source=MetricDatabaseRepository, provides=MetricRepository)
    incidents = provide(source=IncidentDatabaseRepository, provides=IncidentRepository)
    peak_loads = provide(source=PeakLoadDatabaseRepository, provides=PeakLoadRepository)
    thresholds = provide(source=ThresholdReadDatabaseRepository, provides=ThresholdReadRepository)
    avg_loads = provide(source=AverageLoadReadDatabaseRepository, provides=AverageLoadReadRepository)
