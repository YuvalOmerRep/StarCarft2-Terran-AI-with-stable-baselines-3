from sc2.bot_ai import BotAI
from sc2.unit import Unit, AbilityId
import Terran_Strategy as TS
from Feature_Extractors import basic_feature_extractor
import Globals as GB


class RandomTerranBot(BotAI):

    def __init__(self):
        super().__init__()

        self.took_damage = False

        self.strategy = TS.Random_Strategy(self)
        self.features_extractor = basic_feature_extractor(self)

    async def on_step(self, iteration: int):
        if iteration == GB.START_ITERATION:
            all_expansions_locations_sorted = self.start_location.sort_by_distance(self.expansion_locations_list)
            await self.features_extractor.initialize_location_list(all_expansions_locations_sorted)
            await self.strategy.initialize_location_list(all_expansions_locations_sorted)

        elif iteration > GB.START_ITERATION:
            await self.strategy.strategize()

            vec = self.features_extractor.generate_vectors(iteration, iteration)

            print(f"minerals: {vec[0]}")
            print(f"vespene: {vec[1]}")
            print(f"iteration: {vec[2]}")
            print(f"supply used: {vec[3]}")
            print(f"supply cap: {vec[4]}")
            print(f"is_stimmed: {vec[5]}")
            print(f"has_energy: {vec[6]}")
            print(f"TERRANINFANTRYWEAPONSLEVEL1: {vec[7]}")
            print(f"TERRANINFANTRYWEAPONSLEVEL2: {vec[8]}")
            print(f"TERRANINFANTRYWEAPONSLEVEL3: {vec[9]}")
            print(f"TERRANINFANTRYARMORSLEVEL1: {vec[10]}")
            print(f"TERRANINFANTRYARMORSLEVEL2: {vec[11]}")
            print(f"TERRANINFANTRYARMORSLEVEL3: {vec[12]}")
            print(f"STIMPACK: {vec[13]}")
            print(f"SHIELDWALL: {vec[14]}")
            print(f"action_memory: {vec[15: 35]}")
            print(f"ally units:")
            for i, uid in enumerate(GB.terran_unit_list):
                print(f"{uid}: {vec[35 + i]}")
            print(f"ally structures:")
            for i, uid in enumerate(GB.terran_structures_list):
                print(f"{uid}: {vec[41 + i]}")
            print(f"enemy units:")
            for i, uid in enumerate(GB.protoss_units_list):
                print(f"{uid}: {vec[50 + i]}")
            print(f"enemy structures:")
            for i, uid in enumerate(GB.protoss_structures_list):
                print(f"{uid}: {vec[69 + i]}")
            print(f"locations and units: {vec[86: -1]}")

        await self.distribute_workers()

    async def on_building_construction_complete(self, unit: Unit):
        if unit.name == "SupplyDepot":
            self.do(unit(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        return await super().on_building_construction_complete(unit)
