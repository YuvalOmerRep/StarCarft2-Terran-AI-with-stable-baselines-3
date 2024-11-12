from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.data import Difficulty, Race  # difficulty for bots, race for the 1 of 3 races
from sc2.unit import AbilityId, Unit
from sc2.main import run_game  # function that facilitates actually running the agents in games
from sc2.player import Bot, Computer  # wrapper for whether the agent is one of your bots, or a "computer" player
from sc2 import maps  # maps method for loading maps to play in.
import numpy as np

import Utils
from Feature_Extractors import feature_extractor_with_map
import Terran_Strategy
import common
from Terran_Strategy import Random_Strategy
from Utils import Message
from Rewards import Reward_damage_and_unit_with_step_punishment
from Rewards import Reward_end_game
from sc2.ids.unit_typeid import UnitTypeId as UId
from multiprocessing import connection

end_game_reward = 0


class ReinforcementBot(BotAI):  # inherits from BotAI (part of BurnySC2)
    end_game: Reward_end_game
    strategy: Random_Strategy
    conn: connection

    def __init__(self, reward_system, con: connection):
        super().__init__()
        self.end_game = Reward_end_game(self)
        self.strategy = Terran_Strategy.Random_Strategy(self)
        self.features_extractor = feature_extractor_with_map(self)
        self.reward_system = reward_system(self)
        self.units_dict_tags = dict()
        self.my_units_died_since_last_action = []
        self.enemy_units_died_since_last_action = []
        self.units_created_this_frame = []
        self.took_damage = False

        self.conn = con

    async def on_step(self, iteration: int):  # on_step is a method that is called every step of the game.
        if iteration == common.START_ITERATION:
            all_expansions_locations_sorted = self.start_location.sort_by_distance(self.expansion_locations_list)
            await self.features_extractor.initialize_location_list(all_expansions_locations_sorted)
            await self.strategy.initialize_location_list(all_expansions_locations_sorted)
            await self._initialize_tag_dict()

        action_msg = self.conn.recv()
        action = action_msg.action

        await self.distribute_workers()  # put idle workers back to work

        # todo: fix list of commands names
        '''
        0: build_from_command_center
        1: expand_now
        2: build_refinery
        3: build_supply_depo
        4: build_factory
        5: build_barracks
        6: build_engineeringbay
        7: build_marine
        8: build_marauder
        9: build_tank
        10: build_thor
        11: build_reactor
        12: build_techlab
        13: build_armory
        14: upgrade_ground_weapons
        15: upgrade_ground_armor
        16: build_starport
        17: build_from_starport
        18: upgrade_bio
        19: upgrade_marine
        20: stim_army
        21: siege_tanks
        22: attack_enemy_main
        23: attack_enemy_units
        24: attack_enemy_structures
        25: gather_units_at_outpost
        26: gather_units_in_front_of_third
        27: hold_position_all_army
        28: drop_mule
        29: scan_army
        '''

        chosen_action_lst = self.strategy.actions_list[action]
        if iteration <= common.START_ITERATION:
            reward = 0
        else:
            reward = await chosen_action_lst[0]()

        feature_state, game_map = self.features_extractor.generate_vectors(action, iteration)
        state = Utils.create_state(game_map=game_map, game_info=feature_state)

        self.took_damage = False

        reward += self.reward_system.calculate_reward(self.enemy_units_died_since_last_action,
                                                      self.my_units_died_since_last_action,
                                                      self.units_created_this_frame, iteration)

        self.my_units_died_since_last_action = []
        self.enemy_units_died_since_last_action = []
        self.units_created_this_frame = []
        if self.time > common.GAME_TIME_LIMIT - 15:
            global end_game_reward
            self.end_game.update(self.reward_system.get_total_dmg_reward())
            end_game_reward = self.end_game.calculate_reward(self.enemy_units, self.units, self.units, iteration)

        state_reward_msg = Message(state=state, reward=reward)

        if iteration % 1000 == 0:
            print(reward)

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
            self.units_dict_tags[unit.tag] = [unit.is_mine, unit.type_id, is_neutral]

    async def on_building_construction_started(self, unit: Unit):
        self.units_dict_tags[unit.tag] = [unit.is_mine, unit.type_id, False]
        return await super().on_building_construction_started(unit)

    async def on_building_construction_complete(self, unit: Unit):
        if unit.name == "SupplyDepot":
            self.do(unit(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        return await super().on_building_construction_complete(unit)

    async def on_unit_created(self, unit: Unit):

        self.units_dict_tags[unit.tag] = [unit.is_mine, unit.type_id, False]
        if unit.type_id != UId.MULE:
            self.units_created_this_frame.append(unit.type_id)
        return await super().on_unit_created(unit)

    # todo: Might crush game
    async def on_unit_destroyed(self, unit_tag: int):
        try:
            dict_entry = self.units_dict_tags[unit_tag]
            if not dict_entry[2]:
                if dict_entry[0]:
                    self.my_units_died_since_last_action.append(dict_entry[1])
                else:
                    self.enemy_units_died_since_last_action.append(dict_entry[1])
        except KeyError:
            pass

        return await super().on_unit_destroyed(unit_tag)

    async def on_enemy_unit_entered_vision(self, unit: Unit):
        self.units_dict_tags[unit.tag] = [unit.is_mine, unit.type_id, False]
        return await super().on_enemy_unit_entered_vision(unit)

    async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float):
        self.took_damage = True
        return await super().on_unit_took_damage(unit, amount_damage_taken)



def run_game_with_model_bot(conn):
    result = run_game(maps.get("AbyssalReefLE"),
                      [Bot(Race.Terran, ReinforcementBot(Reward_damage_and_unit_with_step_punishment, conn)),
                       Computer(Race.Protoss, Difficulty.Hard)], realtime=False, disable_fog=True)

    if str(result) == "Result.Victory":
        rwd = 500
    elif str(result) == "Result.Tie":
        rwd = end_game_reward
    else:
        rwd = -500

    state = np.zeros(common.OBSERVATION_SPACE_SHAPE_MAP)
    game_done_message = Message(state=state, reward=rwd, done=True)
    conn.send(game_done_message)
