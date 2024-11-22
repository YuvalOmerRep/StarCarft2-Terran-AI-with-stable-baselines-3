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
        if not iteration % 1000:
            print(f"at iteration: {iteration}, reward per time punishment: {reward}, time punishment: {common.step_punishment[iteration]} at final reward: {reward_after_time_punishment}")
        return reward_after_time_punishment

    def _give_reward_for_units_and_structures(self) -> float:
        reward = 0

        for unit in self.agent.units:
            reward_for_unit = self._give_bonus_for_unit_type(unit.type_id, common.UNIT_REWARD_MODIFIER)
            reward += reward_for_unit

        seen_engineering_bays = 0
        for structure in self.agent.structures:
            if structure.type_id == UId.ENGINEERINGBAY:
                seen_engineering_bays += 1
                if seen_engineering_bays > 2:
                    continue
            reward_for_structure = self._give_bonus_for_unit_type(structure.type_id, common.STRUCTURE_REWARD_MODIFIER)
            reward += reward_for_structure

        return reward

    def _give_bonus_for_unit_type(self, uid: UId, reward: float) -> float:
        try:
            cost = self.agent.calculate_cost(uid)
            return (cost.minerals + cost.vespene) * reward
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
