from sc2.bot_ai import BotAI
from sc2.unit import Unit, AbilityId
import Terran_Strategy as TS
from Feature_Extractors import basic_feature_extractor


class RandomTerranBot(BotAI):

    def __init__(self):
        self.took_damage = False
        all_expansions_locations_sorted = self.start_location.sort_by_distance(self.expansion_locations_list)

        self.strategy = TS.Random_Strategy(self, all_expansions_locations_sorted)
        self.features_extractor = basic_feature_extractor(self, all_expansions_locations_sorted)

        super().__init__()

    async def on_step(self, iteration: int):

        await self.strategy.strategize()

        await self.distribute_workers()

    async def on_building_construction_complete(self, unit: Unit):
        if unit.name == "SupplyDepot":
            self.do(unit(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        return await super().on_building_construction_complete(unit)
