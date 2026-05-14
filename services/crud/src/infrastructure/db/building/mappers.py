from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.building import BuildingModel
from shared.dtos.building import CreateBuildingDTO
from shared.entities.building import Building

retort = ConversionRetort()

building__map_from_db = retort.get_converter(BuildingModel, Building)
building__map_to_db = retort.get_converter(Building, BuildingModel)
building__create_mapper = retort.get_converter(
    CreateBuildingDTO,
    BuildingModel,
    recipe=[allow_unlinked_optional(P[BuildingModel].building_id)],
)
