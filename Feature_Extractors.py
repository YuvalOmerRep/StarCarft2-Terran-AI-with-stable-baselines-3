from sc2.bot_ai import BotAI
import numpy as np


class Extractor:
    def __init__(self, bot: BotAI):
        self.bot_to_extract_from = bot

    def update(self, action: int):
        raise NotImplementedError

    def generate_vectors(self) -> np.array:
        raise NotImplementedError


class basic_feature_extractor(Extractor):

    def __init__(self, bot: BotAI):
        super().__init__(bot)
        self.action_taken = -1
        self.ally_workers = -1

    def update(self, action: int):
        self.ally_workers = self.bot_to_extract_from.supply_workers
        self.action_taken = action

    def generate_vectors(self) -> np.array:
        return np.array([self.action_taken, self.ally_workers])
