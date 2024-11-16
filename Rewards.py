from sc2.bot_ai import BotAI
from sc2.units import UnitTypeId as UId
import common

class Rewards:
    def __init__(self, agent: BotAI):
        self.agent = agent

    def calculate_reward(self, enemy_dead, iteration) -> float:
        raise NotImplementedError

    def get_total_dmg_reward(self):
        raise NotImplementedError


class RewardDamageAndUnitWithStepPunishment(Rewards):

    def __init__(self, agent: BotAI):
        super().__init__(agent)
        self.total_dmg_reward = 0

    def get_total_dmg_reward(self):
        return self.total_dmg_reward

    def calculate_reward(self, enemy_dead, iteration) -> float:
        reward = 0
        self._give_reward_for_killing(enemy_dead)
        reward += self._give_reward_for_units_and_structures()
        reward += self.total_dmg_reward
        reward_after_time_punishment = reward * common.step_punishment[iteration]
        if not iteration % 100:
            print(f"at iteration: {iteration}, reward pre time punishment: {reward}, time punishment: {common.step_punishment[iteration-1]} at final reward: {reward_after_time_punishment}")
        return reward_after_time_punishment

    def _give_reward_for_units_and_structures(self) -> float:
        reward = 0

        too_many_engineering_bays = self.agent.units(UId.ENGINEERINGBAY).amount > 2

        for unit in self.agent.units:
            reward_for_unit = self._give_bonus_for_unit_type(unit.type_id)
            if unit.type_id == UId.ENGINEERINGBAY and too_many_engineering_bays:
                reward_for_unit = -reward_for_unit
            reward += reward_for_unit

        return reward

    def _give_bonus_for_unit_type(self, uid: UId) -> float:
        try:
            cost = self.agent.calculate_cost(uid)
            return (cost.minerals + cost.vespene) * common.UNIT_REWARD_MODIFIER
        except:
            return 0

    def _give_worker_actions_bonus(self, reward):
        if self.agent.units(UId.SCV):
            reward += (self.agent.units(UId.SCV).amount - common.STARTING_WORKER_AMOUNT) * common.HARVEST_BONUS
        return reward

    def _give_reward_for_killing(self, enemy_dead):
        for enemy_dead_unit in enemy_dead:

            try:
                dead_unit_cost = self.agent.calculate_cost(enemy_dead_unit)
                potential_reward = \
                    (dead_unit_cost.minerals + dead_unit_cost.vespene) * common.ENEMY_UNIT_KILLED_REWARD_MODIFIER

                self.total_dmg_reward += potential_reward
            except:
                continue
