from dataclasses import dataclass


@dataclass
class EnergyBalanceResult:
    loss_kwh: float
    loss_percent: float


class EnergyBalanceCalculator:
    """Pure, stateless. common_kwh − individual_sum_kwh = losses."""

    def compute(
        self, common_kwh: float, individual_sum_kwh: float
    ) -> EnergyBalanceResult:
        loss_kwh = common_kwh - individual_sum_kwh
        # Avoid division by zero when common meter reads zero
        loss_percent = (loss_kwh / common_kwh * 100) if common_kwh > 0 else 0.0
        return EnergyBalanceResult(loss_kwh=loss_kwh, loss_percent=loss_percent)
