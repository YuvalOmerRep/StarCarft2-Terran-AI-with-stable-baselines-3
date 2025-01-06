from sc2.bot_ai import BotAI
import numpy as np
from sc2.ids.unit_typeid import UnitTypeId as UId
from sc2.ids.buff_id import BuffId as BId
from sc2.ids.upgrade_id import UpgradeId as UpId
import common
from Utils import MultipleDiscreteMemory, get_x_y_of_pos


def get_amount(uid: UId, group) -> int:
    if group(uid):
        return group(uid).amount
    else:
        return 0


class Extractor:
    def __init__(self, bot: BotAI):
        self.bot_to_extract_from = bot

    def generate_vectors(self, action: list[int], iteration: int) -> np.array:
        is_stimmed = self.get_is_stimmed()
        has_energy = self.command_center_has_energy_for_ability()


        vector = [self.bot_to_extract_from.minerals, self.bot_to_extract_from.vespene, iteration,
                  self.bot_to_extract_from.supply_used, self.bot_to_extract_from.supply_cap, is_stimmed, has_energy,
                  self.bot_to_extract_from.already_pending_upgrade(UpId.TERRANINFANTRYWEAPONSLEVEL1),
                  self.bot_to_extract_from.already_pending_upgrade(UpId.TERRANINFANTRYWEAPONSLEVEL2),
                  self.bot_to_extract_from.already_pending_upgrade(UpId.TERRANINFANTRYWEAPONSLEVEL3),
                  self.bot_to_extract_from.already_pending_upgrade(UpId.TERRANINFANTRYARMORSLEVEL1),
                  self.bot_to_extract_from.already_pending_upgrade(UpId.TERRANINFANTRYARMORSLEVEL2),
                  self.bot_to_extract_from.already_pending_upgrade(UpId.TERRANINFANTRYARMORSLEVEL3),
                  self.bot_to_extract_from.already_pending_upgrade(UpId.STIMPACK),
                  self.bot_to_extract_from.already_pending_upgrade(UpId.SHIELDWALL)
                  ]

        vector += \
            [get_amount(uid, self.bot_to_extract_from.units)
             for uid in common.terran_unit_list]  # ally_units

        vector += \
            [get_amount(uid, self.bot_to_extract_from.structures)
             for uid in common.terran_structures_list]  # ally_buildings

        vector += \
            [get_amount(uid, self.bot_to_extract_from.enemy_units)
             for uid in common.protoss_units_list]  # enemy_units

        vector += \
            [get_amount(uid, self.bot_to_extract_from.enemy_structures)
             for uid in common.protoss_structures_list]  # enemy_buildings

        return vector

    def get_is_stimmed(self):
        for marine in self.bot_to_extract_from.units(UId.MARINE):
            if marine.has_buff(BId.STIMPACK):
                return 1

        for marauder in self.bot_to_extract_from.units(UId.MARAUDER):
            if marauder.has_buff(BId.STIMPACK):
                return 1

        return 0

    def command_center_has_energy_for_ability(self):
        for townhall in self.bot_to_extract_from.townhalls:
            if townhall.energy >= common.ENERGY_FOR_MULE_OR_SCAN:
                return 1
        return 0


class basic_feature_extractor(Extractor):

    def __init__(self, bot: BotAI):
        super().__init__(bot)
        self.locations_sorted = []

    async def initialize_location_list(self, locations_sorted):
        self.locations_sorted = locations_sorted

    def generate_vectors(self, actions: list[int], iteration: int) -> np.array:
        vector = super().generate_vectors(actions, iteration)

        vector += self.get_amounts_from_group_relative_to_expansions()  # "radar" system
        # for getting locations of ally and enemy units and structures

        return np.array(vector)

    def get_amounts_from_group_relative_to_expansions(self):
        result = []

        for location in self.locations_sorted:
            result.append(amount_from_location_and_group(self.bot_to_extract_from.units, location))
            result.append(amount_from_location_and_group(self.bot_to_extract_from.structures, location))
            result.append(amount_from_location_and_group(self.bot_to_extract_from.enemy_units, location))
            result.append(amount_from_location_and_group(self.bot_to_extract_from.enemy_structures, location))

        if not len(result):
            return [-1 for i in range(56)]

        return result


def amount_from_location_and_group(group, location):
    ally_units_in_location_radius = \
        group.closer_than(common.RADIUS_FROM_LOCATION, location)
    if ally_units_in_location_radius:
        return ally_units_in_location_radius.amount
    else:
        return 0


class feature_extractor_with_map(Extractor):

    def __init__(self, bot: BotAI):
        super().__init__(bot)
        self.action_memory = MultipleDiscreteMemory()
        self.locations_sorted = []

    async def initialize_location_list(self, locations_sorted):
        self.locations_sorted = locations_sorted

    def get_is_stimmed(self):
        for marine in self.bot_to_extract_from.units(UId.MARINE):
            if marine.has_buff(BId.STIMPACK):
                return 1

        for marauder in self.bot_to_extract_from.units(UId.MARAUDER):
            if marauder.has_buff(BId.STIMPACK):
                return 1

        return 0

    def command_center_has_energy_for_ability(self):
        for townhall in self.bot_to_extract_from.townhalls:
            if townhall.energy >= common.ENERGY_FOR_MULE_OR_SCAN:
                return 1
        return 0

    def generate_vectors(self, actions: list[int], iteration: int) -> np.array:
        vector = super().generate_vectors(actions, iteration)
        self.action_memory.register_action(actions=actions, iteration=iteration)
        memory = self.action_memory.get_memory()
        game_map = self.generate_map()
        return np.append(memory, vector), game_map

    def generate_map(self):
        game_map = np.zeros((self.bot_to_extract_from.game_info.map_size[0],
                        self.bot_to_extract_from.game_info.map_size[1], 3), dtype=np.uint8)

        # draw the minerals:
        for mineral in self.bot_to_extract_from.mineral_field:
            pos = mineral.position
            c = common.MINERAL_COLOR
            fraction = mineral.mineral_contents / 1800
            x, y = get_x_y_of_pos(pos, game_map.shape)
            if mineral.is_visible:
                game_map[y][x] = [int(fraction * i) for i in c]
            else:
                game_map[y][x] = [20, 75, 50]

                # draw the enemy start location:
        for enemy_start_location in self.bot_to_extract_from.enemy_start_locations:
            pos = enemy_start_location
            x, y = get_x_y_of_pos(pos, game_map.shape)
            c = [0, 0, 255]
            game_map[y][x] = c

        # draw the enemy units:
        for enemy_unit in self.bot_to_extract_from.enemy_units:
            pos = enemy_unit.position
            x, y = get_x_y_of_pos(pos, game_map.shape)
            c = common.ENEMY_UNIT_COLOR
            # get unit health fraction:
            fraction = enemy_unit.health / enemy_unit.health_max if enemy_unit.health_max > 0 else 0.0001
            game_map[y][x] = [int(fraction * i) for i in c]

        # draw the enemy structures:
        for enemy_structure in self.bot_to_extract_from.enemy_structures:
            pos = enemy_structure.position
            x, y = get_x_y_of_pos(pos, game_map.shape)
            c = common.ENEMY_STRUCTURE_COLOR
            # get structure health fraction:
            fraction = enemy_structure.health / enemy_structure.health_max if enemy_structure.health_max > 0 else 0.0001
            game_map[y][x] = [int(fraction * i) for i in c]

        # draw our structures:
        for our_structure in self.bot_to_extract_from.structures:
            # if it's a nexus:
            if our_structure.type_id == UId.NEXUS:
                pos = our_structure.position
                x, y = get_x_y_of_pos(pos, game_map.shape)
                c = common.ALLY_BASE_COLOR
                # get structure health fraction:
                fraction = our_structure.health / our_structure.health_max if our_structure.health_max > 0 else 0.0001
                game_map[y][x] = [int(fraction * i) for i in c]

            else:
                pos = our_structure.position
                x, y = get_x_y_of_pos(pos, game_map.shape)
                c = common.ALLY_STRUCTURE_COLOR
                # get structure health fraction:
                fraction = our_structure.health / our_structure.health_max if our_structure.health_max > 0 else 0.0001
                game_map[y][x] = [int(fraction * i) for i in c]

        # draw the vespene geysers:
        for vespene in self.bot_to_extract_from.vespene_geyser:
            # draw these after buildings, since assimilators go over them.
            # tried to denote some way that assimilator was on top, couldnt
            # come up with anything. Tried by positions, but the positions arent identical. ie:
            # vesp position: (50.5, 63.5)
            # bldg positions: [(64.369873046875, 58.982421875), (52.85693359375, 51.593505859375),...]
            pos = vespene.position
            x, y = get_x_y_of_pos(pos, game_map.shape)
            c = common.VESPENE_COLOR
            fraction = vespene.vespene_contents / 2250

            if vespene.is_visible:
                game_map[y][x] = [int(fraction * i) for i in c]
            else:
                game_map[y][x] = [50, 20, 75]

        # draw our units:
        for our_unit in self.bot_to_extract_from.units:
            if our_unit.type_id in [UId.SCV, UId.MARINE, UId.SIEGETANK, UId.SIEGETANKSIEGED,
                                    UId.MEDIVAC, UId.MARAUDER, UId.THOR]:

                pos = our_unit.position
                x, y = get_x_y_of_pos(pos, game_map.shape)
                c = common.MARINE_COLOR
                # get health:
                fraction = our_unit.health / our_unit.health_max if our_unit.health_max > 0 else 0.0001
                game_map[y][x] = [int(fraction * i) for i in c]


            else:
                pos = our_unit.position
                x, y = get_x_y_of_pos(pos, game_map.shape)
                c = common.SCV_COLOR
                # get health:
                fraction = our_unit.health / our_unit.health_max if our_unit.health_max > 0 else 0.0001
                game_map[y][x] = [int(fraction * i) for i in c]

                # show map with opencv, resized to be larger:
                # horizontal flip:

        return game_map
