from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.data import Difficulty, Race  # difficulty for bots, race for the 1 of 3 races
from sc2.unit import AbilityId, Unit
from sc2.main import run_game  # function that facilitates actually running the agents in games
from sc2.player import Bot, Computer  # wrapper for whether or not the agent is one of your bots, or a "computer" player
from sc2 import maps  # maps method for loading maps to play in.
import numpy as np
import sys
import pickle
from Feature_Extractors import basic_feature_extractor
import Terran_Strategy as TS
import Globals as GB
from Rewards import Reward_damage_and_unit_with_step_punishment
from Rewards import Reward_end_game
from sc2.ids.unit_typeid import UnitTypeId as UId

end_game_reward = 0


class Reinforcement_bot(BotAI):  # inherits from BotAI (part of BurnySC2)
    def __init__(self, reward_system):
        super().__init__()
        self.end_game = Reward_end_game(self)
        self.strategy = TS.Random_Strategy(self)
        self.features_extractor = basic_feature_extractor(self)
        self.reward_system = reward_system(self)
        self.units_dict_tags = dict()
        self.my_units_died_since_last_action = []
        self.enemy_units_died_since_last_action = []
        self.units_created_this_frame = []
        self.took_damage = False

    async def on_step(self, iteration: int):  # on_step is a method that is called every step of the game.
        if iteration == GB.START_ITERATION:
            await self._initialize_tag_dict()

        no_action = True
        while no_action:
            try:
                with open('state_rwd_action.pkl', 'rb') as f:
                    state_rwd_action = pickle.load(f)

                    if state_rwd_action['action'] is None:
                        # No action to execute, continue waiting
                        no_action = True
                    else:
                        # Action found, continue to execute
                        no_action = False
            except:
                pass

        await self.distribute_workers()  # put idle workers back to work

        action = state_rwd_action['action']
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

        reward = await chosen_action_lst[0]()

        feature_state = self.features_extractor.generate_vectors(action)

        self.took_damage = False

        reward += self.reward_system.calculate_reward(self.enemy_units_died_since_last_action,
                                                      self.my_units_died_since_last_action,
                                                      self.units_created_this_frame, iteration)

        self.my_units_died_since_last_action = []
        self.enemy_units_died_since_last_action = []
        self.units_created_this_frame = []
        if self.time > GB.GAME_TIME_LIMIT - 15:
            global end_game_reward
            end_game_reward = self.end_game.calculate_reward(self.enemy_units, self.units, self.units, iteration)

        data = {"state": feature_state, "reward": reward,
                "action": None, "done": False}  # empty action waiting for the next one!

        if iteration % 1000 == 0:
            print(reward)

        with open('state_rwd_action.pkl', 'wb') as f:
            pickle.dump(data, f)

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


result = run_game(maps.get("JagannathaAIE"),
                  [Bot(Race.Terran, Reinforcement_bot(Reward_damage_and_unit_with_step_punishment)),
                   Computer(Race.Protoss, Difficulty.Easy)], realtime=False)

if str(result) == "Result.Victory":
    rwd = 500
elif str(result) == "Result.Tie":
    rwd = end_game_reward
    print(rwd)
else:
    rwd = -500

with open("results.txt", "a") as f:
    f.write(f"{result}\n")

state = np.zeros(GB.OBSERVATION_SPACE_SHAPE)
observation = state
data = {"state": state, "reward": rwd, "action": None,
        "done": True}  # empty action waiting for the next one!
with open('state_rwd_action.pkl', 'wb') as f:
    pickle.dump(data, f)

sys.exit()
