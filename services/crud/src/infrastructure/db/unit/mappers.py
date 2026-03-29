from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.unit import UnitModel
from shared.dtos.unit import CreateUnitDTO
from shared.entities.unit import Unit

retort = ConversionRetort()

unit__map_from_db = retort.get_converter(UnitModel, Unit)
unit__map_to_db = retort.get_converter(Unit, UnitModel)
unit__create_mapper = retort.get_converter(
    CreateUnitDTO,
    UnitModel,
    recipe=[allow_unlinked_optional(P[UnitModel].unit_id)],
)
