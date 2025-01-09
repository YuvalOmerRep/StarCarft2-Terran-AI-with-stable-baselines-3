from sc2.bot_ai import BotAI
from sc2.units import UnitTypeId as UId
import common

class Rewards:
    def __init__(self, agent: BotAI):
        self.agent = agent

    def calculate_reward(self, enemy_dead: list[UId], ally_dead: list[tuple[UId, bool]], iteration: int, reward_from_action: float) -> float:
        raise NotImplementedError

    def get_total_dmg_reward(self):
        raise NotImplementedError


class RewardDamageAndUnitWithStepPunishment(Rewards):

    def __init__(self, agent: BotAI):
        super().__init__(agent)
        self.accumulative_reward = 0

    def get_total_dmg_reward(self):
        return self.accumulative_reward

    def calculate_reward(self, enemy_dead: list[UId], ally_dead: list[tuple[UId, bool]], iteration: int, reward_from_action: float) -> float:
        self.accumulative_reward += reward_from_action
        reward = self.accumulative_reward
        self._give_reward_for_killing(enemy_dead)
        self._give_punishment_for_dying(ally_dead)
        reward += self._give_reward_for_units()
        reward_after_time_punishment = reward * common.step_punishment[iteration]
        if not iteration % 1000:
            print(f"at iteration: {iteration}, reward per time punishment: {reward}, time punishment: {common.step_punishment[iteration]} at final reward: {reward_after_time_punishment}")
        return reward_after_time_punishment

    def _give_reward_for_units(self) -> float:
        reward = 0

        for unit in self.agent.units:
            if unit.is_structure or unit.type_id == UId.SCV:
                continue
            reward += self._give_bonus_for_unit_type_and_upgrade_levels(unit.type_id, common.UNIT_REWARD_MODIFIER, unit.attack_upgrade_level, unit.armor_upgrade_level)

        scv_reward = self._give_bonus_for_unit_type_and_upgrade_levels(UId.SCV, common.UNIT_REWARD_MODIFIER, 0, 0)
        reward += scv_reward * (self.agent.supply_workers - common.STARTING_WORKER_AMOUNT)
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

    def _give_reward_for_killing(self, enemy_dead: list[UId]):
        for enemy_dead_unit in enemy_dead:

            try:
                dead_unit_cost = self.agent.calculate_cost(enemy_dead_unit)
                reward = \
                    (dead_unit_cost.minerals + dead_unit_cost.vespene) * common.ENEMY_UNIT_KILLED_REWARD_MODIFIER

                self.accumulative_reward += reward
            except:
                continue

    def _give_punishment_for_dying(self, ally_dead: list[tuple[UId, bool]]):
        for ally_dead_unit in ally_dead:

            try:
                if ally_dead_unit[1]:
                    dead_unit_cost = self.agent.calculate_cost(ally_dead_unit[0])
                    punishment = \
                        (dead_unit_cost.minerals + dead_unit_cost.vespene) * common.ALLY_UNIT_KILLED_REWARD_MODIFIER

                    self.accumulative_reward -= punishment
            except:
                continue
