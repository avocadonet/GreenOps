from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.energy_balance import EnergyBalanceModel
from shared.dtos.energy_balance import CreateEnergyBalanceDTO
from shared.entities.energy_balance import EnergyBalance

retort = ConversionRetort()

energy_balance__map_from_db = retort.get_converter(EnergyBalanceModel, EnergyBalance)
energy_balance__create_mapper = retort.get_converter(
    CreateEnergyBalanceDTO,
    EnergyBalanceModel,
    recipe=[allow_unlinked_optional(P[EnergyBalanceModel].balance_id)],
)
