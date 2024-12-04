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
        reward += self._give_reward_for_units()
        reward += self.total_dmg_reward
        reward_after_time_punishment = reward * common.step_punishment[iteration]
        if not iteration % 1000:
            print(f"at iteration: {iteration}, reward per time punishment: {reward}, time punishment: {common.step_punishment[iteration]} at final reward: {reward_after_time_punishment}")
        return reward_after_time_punishment

    def _give_reward_for_units(self) -> float:
        reward = 0

        for unit in self.agent.units:
            if unit.is_structure:
                continue
            reward += self._give_bonus_for_unit_type_and_upgrade_levels(unit.type_id, common.UNIT_REWARD_MODIFIER, unit.attack_upgrade_level, unit.armor_upgrade_level)

        return reward

    def _give_bonus_for_unit_type_and_upgrade_levels(self, uid: UId, reward_modifier: float, attack_upgrade_level: int, armor_upgrade_level: int) -> float:
        try:
            cost = self.agent.calculate_cost(uid)
            reward_for_unit = (cost.minerals + cost.vespene) * reward_modifier
            reward_for_unit += reward_for_unit * ((attack_upgrade_level + armor_upgrade_level) * common.UNIT_UPGRADE_REWARD_MODIFIER)
            return reward_for_unit
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
