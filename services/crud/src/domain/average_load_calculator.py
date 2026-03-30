from dataclasses import dataclass


@dataclass
class AverageLoadResult:
    mean_value: float


class AverageLoadCalculator:
    """Pure, stateless. Returns None when there are no data points."""

    def compute(self, values: list[float]) -> AverageLoadResult | None:
        if not values:
            return None
        return AverageLoadResult(mean_value=sum(values) / len(values))
