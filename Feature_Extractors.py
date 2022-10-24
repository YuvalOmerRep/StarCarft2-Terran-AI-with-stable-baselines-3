from sc2.bot_ai import BotAI
import numpy as np
from sc2.ids.unit_typeid import UnitTypeId as UId
import Globals


class Extractor:
    def __init__(self, bot: BotAI):
        self.bot_to_extract_from = bot

    def generate_vectors(self, action: int) -> np.array:
        raise NotImplementedError


def get_amount(uid: UId, group) -> int:
    if group(uid):
        return group(uid).amount
    else:
        return 0


class basic_feature_extractor(Extractor):

    def __init__(self, bot: BotAI):
        super().__init__(bot)

    def generate_vectors(self, action: int) -> np.array:
        vector = [action, self.bot_to_extract_from.minerals, self.bot_to_extract_from.vespene]
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

        return np.array(vector)
