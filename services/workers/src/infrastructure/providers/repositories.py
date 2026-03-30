from dishka import Provider, Scope, provide

from infrastructure.db.average_load.repository import AverageLoadReadDatabaseRepository
from infrastructure.db.incident.repository import IncidentDatabaseRepository
from infrastructure.db.metric.repository import MetricDatabaseRepository
from infrastructure.db.peak_load.repository import PeakLoadDatabaseRepository
from infrastructure.db.threshold.repository import ThresholdReadDatabaseRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    metrics = provide(MetricDatabaseRepository)
    incidents = provide(IncidentDatabaseRepository)
    peak_loads = provide(PeakLoadDatabaseRepository)
    thresholds = provide(ThresholdReadDatabaseRepository)
    avg_loads = provide(AverageLoadReadDatabaseRepository)
