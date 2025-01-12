from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.data import Difficulty, Race, Result  # difficulty for bots, race for the 1 of 3 races
from sc2.unit import AbilityId, Unit
from sc2.main import run_game  # function that facilitates actually running the agents in games
from sc2.player import Bot, Computer  # wrapper for whether the agent is one of your bots, or a "computer" player
from sc2 import maps  # maps method for loading maps to play in.

import Utils
from Feature_Extractors import feature_extractor_with_map
import Terran_Strategy
import common
from Terran_Strategy import Random_Strategy
from Utils import Message
from Rewards import RewardDamageAndUnitWithStepPunishment, Rewards
from sc2.ids.unit_typeid import UnitTypeId as UId
from multiprocessing import connection


last_iteration = 0

class ReinforcementBot(BotAI):  # inherits from BotAI (part of BurnySC2)
    strategy: Random_Strategy
    conn: connection
    reward_system: Rewards

    def __init__(self, reward_system, con: connection):
        super().__init__()
        self.strategy = Terran_Strategy.Random_Strategy(self)
        self.features_extractor = feature_extractor_with_map(self)
        self.reward_system = reward_system(self)
        self.units_dict_tags: dict[int, tuple[bool, UId, bool, bool]] = dict()
        self.my_units_died_since_last_action: list[tuple[UId, bool]] = []
        self.enemy_units_died_since_last_action: list[UId] = []
        self.units_created_this_frame: list[UId] = []
        self.took_damage = False

        self.conn = con

    async def on_step(self, iteration: int):
        global last_iteration
        last_iteration = iteration
        # on_step is a method that is called every step of the game.
        if iteration == common.START_ITERATION:
            all_expansions_locations_sorted = self.start_location.sort_by_distance(self.expansion_locations_list)
            await self.features_extractor.initialize_location_list(all_expansions_locations_sorted)
            await self.strategy.initialize_location_list(all_expansions_locations_sorted)
            await self._initialize_tag_dict()

        action_msg = self.conn.recv()
        action = action_msg.action

        if not iteration % 100:
            await self.distribute_workers()  # put idle workers back to work

        reward_from_action = 0
        if iteration > common.START_ITERATION:
            reward_from_action += await self.strategy.strategize(action)

        feature_state, game_map = self.features_extractor.generate_vectors(action, iteration)
        state = Utils.create_state(game_map=game_map, game_info=feature_state)

        self.took_damage = False

        reward = self.reward_system.calculate_reward(self.enemy_units_died_since_last_action, self.my_units_died_since_last_action, iteration, reward_from_action)

        self.my_units_died_since_last_action.clear()
        self.enemy_units_died_since_last_action.clear()
        self.units_created_this_frame.clear()

        state_reward_msg = Message(state=state, reward=reward)

        self.conn.send(state_reward_msg)

    async def _initialize_tag_dict(self):
        await self._initialize_one_group_tag_dict(self.units)

        await self._initialize_one_group_tag_dict(self.structures)

        await self._initialize_one_group_tag_dict(self.enemy_units)

        await self._initialize_one_group_tag_dict(self.enemy_structures)

        await self._initialize_one_group_tag_dict(self.resources, True)

        await self._initialize_one_group_tag_dict(self.destructables, True)

    async def _initialize_one_group_tag_dict(self, group, is_neutral=False):
        for unit in group:
            self.units_dict_tags[unit.tag] = (unit.is_mine, unit.type_id, is_neutral, unit.is_structure)

    async def on_building_construction_started(self, unit: Unit):
        self.units_dict_tags[unit.tag] = (unit.is_mine, unit.type_id, False, unit.is_structure)
        return await super().on_building_construction_started(unit)

    async def on_building_construction_complete(self, unit: Unit):
        if unit.name == "SupplyDepot":
            self.do(unit(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        return await super().on_building_construction_complete(unit)

    async def on_unit_created(self, unit: Unit):

        self.units_dict_tags[unit.tag] = (unit.is_mine, unit.type_id, False, unit.is_structure)
        if unit.type_id != UId.MULE:
            self.units_created_this_frame.append(unit.type_id)
        return await super().on_unit_created(unit)

    async def on_unit_destroyed(self, unit_tag: int):
        try:
            dict_entry = self.units_dict_tags[unit_tag]
            if not dict_entry[2]:
                if dict_entry[0]:
                    self.my_units_died_since_last_action.append((dict_entry[1], dict_entry[3]))
                else:
                    self.enemy_units_died_since_last_action.append(dict_entry[1])
        except KeyError:
            pass

        return await super().on_unit_destroyed(unit_tag)

    async def on_enemy_unit_entered_vision(self, unit: Unit):
        self.units_dict_tags[unit.tag] = (unit.is_mine, unit.type_id, False, unit.is_structure)
        return await super().on_enemy_unit_entered_vision(unit)

    async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float):
        self.took_damage = True
        return await super().on_unit_took_damage(unit, amount_damage_taken)



def run_game_with_model_bot(conn, difficulty: Difficulty):
    result = run_game(maps.get("AbyssalReefLE"),
                      [Bot(Race.Terran, ReinforcementBot(RewardDamageAndUnitWithStepPunishment, conn)),
                       Computer(Race.Protoss, difficulty)], realtime=False, disable_fog=True)


    if result == Result.Victory:
        print("\033[92mWinner Winner chicken dinner!\033[0m")
        reward = 1000000
    elif result == Result.Tie:
        print("\033[92mTie that Tie!\033[0m")
        reward = 0
    else:
        print("\033[92mLost Once again\033[0m")
        reward = -100000


    reward_after_time_punishment =  reward * common.step_punishment[last_iteration]
    print(f"at end of match when iteration: {last_iteration}, reward per time punishment: {reward}, time punishment: {common.step_punishment[last_iteration]} at final reward: {reward_after_time_punishment}")

    game_done_message = Message(state=Utils.create_state(), reward=reward_after_time_punishment, done=True)
    conn.send(game_done_message)
