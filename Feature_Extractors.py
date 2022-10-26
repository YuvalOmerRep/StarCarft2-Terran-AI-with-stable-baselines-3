from sc2.bot_ai import BotAI
import numpy as np
from sc2.ids.unit_typeid import UnitTypeId as UId
from sc2.ids.buff_id import BuffId as BId
from sc2.ids.upgrade_id import UpgradeId as UpId
import Globals


class Extractor:
    def __init__(self, bot: BotAI):
        self.bot_to_extract_from = bot

    def generate_vectors(self, action: int, iteration: int) -> np.array:
        raise NotImplementedError

    async def initialize_location_list(self, locations_sorted):
        raise NotImplementedError


def get_amount(uid: UId, group) -> int:
    if group(uid):
        return group(uid).amount
    else:
        return 0


class basic_feature_extractor(Extractor):

    def __init__(self, bot: BotAI):
        super().__init__(bot)
        self.action_memory = [-1 for i in range(Globals.MEMORY_SIZE)]
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
            if townhall.energy >= Globals.ENERGY_FOR_MULE_OR_SCAN:
                return 1
        return 0

    def generate_vectors(self, action: int, iteration: int) -> np.array:
        is_stimmed = self.get_is_stimmed()
        has_energy = self.command_center_has_energy_for_ability()

        self.action_memory.pop(0)
        self.action_memory.append(action)

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

        vector += self.action_memory

        vector += \
            [get_amount(i, self.bot_to_extract_from.units)
             for i in Globals.terran_unit_list]  # ally_units

        vector += \
            [get_amount(i, self.bot_to_extract_from.structures)
             for i in Globals.terran_structures_list]  # ally_buildings

        vector += \
            [get_amount(i, self.bot_to_extract_from.enemy_units)
             for i in Globals.protoss_units_list]  # enemy_units

        vector += \
            [get_amount(i, self.bot_to_extract_from.enemy_structures)
             for i in Globals.protoss_structures_list]  # enemy_buildings

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
        group.closer_than(Globals.RADIUS_FROM_LOCATION, location)
    if ally_units_in_location_radius:
        return ally_units_in_location_radius.amount
    else:
        return 0
