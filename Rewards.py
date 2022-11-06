from sc2.bot_ai import BotAI
from sc2.units import UnitTypeId as UId
import Globals as GB
from math import floor


class Rewards:
    def __init__(self, agent: BotAI):
        self.agent = agent

    def calculate_reward(self, enemy_dead, ally_dead, created_units, iteration) -> float:
        raise NotImplementedError

    def get_total_dmg_reward(self):
        raise NotImplementedError


class Reward_damage_and_unit_with_step_punishment(Rewards):

    def __init__(self, agent: BotAI):
        super().__init__(agent)
        self.damage_reward = 0
        self.damage_punishment = 0
        self.total_dmg_reward = 0

    def get_total_dmg_reward(self):
        return self.total_dmg_reward

    def calculate_reward(self, enemy_dead, ally_dead, created_units, iteration) -> float:
        reward = 0
        self._give_reward_for_killing(enemy_dead)

        self._give_bonus_for_creation(created_units, reward)

        reward += self.damage_reward

        reward -= self.damage_punishment

        self.total_dmg_reward += self.damage_reward
        self.total_dmg_reward -= self.damage_punishment

        reward += GB.step_punishment[iteration]

        self.damage_reward = 0

        return reward

    def _give_bonus_for_creation(self, units, reward):
        for unit in units:
            self._give_bonus_for_unit_type(unit, reward)

    def _give_bonus_for_unit_type(self, uid: UId, reward):
        try:
            cost = self.agent.calculate_cost(uid)
        except:
            return 0
        reward += (cost.minerals + cost.vespene) * GB.UNIT_REWARD_MODIFIER
        return reward

    def _give_worker_actions_bonus(self, reward):
        if self.agent.units(UId.SCV):
            reward += (self.agent.units(UId.SCV).amount - GB.STARTING_WORKER_AMOUNT) * GB.HARVEST_BONUS
        return reward

    def _give_reward_for_killing(self, enemy_dead):
        for enemy_dead_unit in enemy_dead:

            try:
                dead_unit_cost = self.agent.calculate_cost(enemy_dead_unit)
                potential_reward = \
                    (dead_unit_cost.minerals + dead_unit_cost.vespene) * GB.ENEMY_UNIT_KILLED_REWARD_MODIFIER

                self.damage_reward += potential_reward
            except:
                continue

    def _give_punishment_for_dying(self, ally_dead):
        for ally_dead_unit in ally_dead:

            try:
                dead_unit_cost = self.agent.calculate_cost(ally_dead_unit)
                potential_reward = \
                    (dead_unit_cost.minerals + dead_unit_cost.vespene) * GB.ALLY_UNIT_KILLED_PUNISHMENT_MODIFIER

                self.damage_punishment += potential_reward
            except:
                continue


class Reward_end_game(Rewards):

    def __init__(self, agent: BotAI):
        super().__init__(agent)
        self.damage_reward = 0
        self.damage_punishment = 0
        self.total_damage_dealt_in_game = 0

    def update(self, dmg_this_round):
        self.total_damage_dealt_in_game += dmg_this_round

    def calculate_reward(self, enemy, ally, created_units, iteration) -> float:
        reward = 0

        self._give_reward_for_unit(enemy)

        reward -= self.damage_reward

        self.damage_reward = 0

        self._give_reward_for_unit(ally)

        reward += self.damage_reward

        self.damage_reward = 0

        reward += self.total_damage_dealt_in_game

        return reward

    def _give_reward_for_unit(self, units):
        for unit in units:

            try:
                dead_unit_cost = self.agent.calculate_cost(unit.type_id)
                potential_reward = \
                    (dead_unit_cost.minerals + dead_unit_cost.vespene) * GB.END_GAME_PUN_REWARD

                self.damage_reward += potential_reward
            except:
                continue
