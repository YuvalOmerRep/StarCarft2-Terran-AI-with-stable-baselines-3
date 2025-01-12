import asyncio
import random

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId as UId
from sc2.ids.upgrade_id import UpgradeId as UpId
from sc2.unit import AbilityId
import common as GB


class Terran_Strategy:
    def __init__(self, agent: BotAI):
        self.agent = agent

    async def strategize(self, actions: list[int]):
        raise NotImplementedError

    async def initialize_location_list(self, locations_sorted):
        raise NotImplementedError


async def find_from_group_with_reactor(structures_to_check, unit_to_train: UId):
    """
    Iterate over a given group of structures and train a unit if a structure has a reactor

    :param structures_to_check: the group of structures to iterate over
    :param unit_to_train: the unit to train if a structure with a reactor is found
    :return:
    """
    for structure in structures_to_check:
        if structure.has_reactor:
            structure.train(unit_to_train, queue=True)
            return 1

    return 0


class Random_Strategy(Terran_Strategy):
    def __init__(self, agent: BotAI):
        """
        The __init__ method of the Random_Strategy class,

        :param agent: The agent that acts according to this strategy
        """
        super().__init__(agent)
        self.is_sieged = False
        self.locations_sorted = []

        self.build_actions = [
            [self.expand_now, "expand_now"],
            [self.build_refinery, "build_refinery"],
            [self.create_build_structure(UId.SUPPLYDEPOT), "build_supply_depo"],
            [self.create_build_structure(UId.FACTORY, add_on=True), "build_factory"],
            [self.create_build_structure(UId.BARRACKS, add_on=True), "build_barracks"],
            [self.create_build_structure(UId.ENGINEERINGBAY), "build_engineeringbay"],
            [self.create_build_structure(UId.ARMORY), "build_armory"],
            [self.create_build_structure(UId.STARPORT, add_on=True), "build_starport"],
            [self.create_build_structure(UId.FUSIONCORE), "build_fusioncore"],
            [self.create_build_addon(UId.REACTOR, UId.BARRACKS, AbilityId.BUILD_REACTOR_BARRACKS), "build_barracks_reactor"],
            [self.create_build_addon(UId.TECHLAB, UId.BARRACKS, AbilityId.BUILD_TECHLAB_BARRACKS), "build_barracks_techlab"],
            [self.create_build_addon(UId.FACTORYREACTOR, UId.FACTORY, AbilityId.BUILD_REACTOR_FACTORY), "build_factory_reactor"],
            [self.create_build_addon(UId.FACTORYTECHLAB, UId.FACTORY, AbilityId.BUILD_TECHLAB_FACTORY), "build_factory_techlab"],
            [self.create_build_addon(UId.STARPORTREACTOR, UId.STARPORT, AbilityId.BUILD_REACTOR_STARPORT), "build_starport_reactor"],
            [self.create_build_addon(UId.STARPORTTECHLAB, UId.STARPORT, AbilityId.BUILD_TECHLAB_STARPORT), "build_starport_techlab"],
            [self.upgrade_to_orbital, "upgrade_to_orbital"],
            [self.noop, "don't build structure"],
        ]

        self.manufacture_unit_actions = [
            [self.build_worker, "build_worker"],
            [self.create_build_unit_from_structure(UId.BARRACKS, UId.MARINE), "build_marine"],
            [self.create_build_unit_from_structure(UId.BARRACKS, UId.MARAUDER), "build_marauder"],
            [self.create_build_unit_from_structure(UId.FACTORY, UId.SIEGETANK), "build_tank"],
            [self.create_build_unit_from_structure(UId.FACTORY, UId.THOR), "build_thor"],
            [self.create_build_unit_from_structure(UId.STARPORT, UId.MEDIVAC), "build_medivac"],
            [self.create_build_unit_from_structure(UId.STARPORT, UId.BATTLECRUISER), "build_battle_cruiser"],
            [self.noop, "don't build unit"],
        ]

        self.research_upgrade_actions = [
            [self.upgrade_ground_weapons, "upgrade_ground_weapons"],
            [self.upgrade_ground_armor, "upgrade_ground_armor"],
            [self.upgrade_bio, "upgrade_bio"],
            [self.upgrade_marine, "upgrade_marine"],
            [self.noop, "don't research"],
        ]

        self.command_center_abilities = [
            [self.drop_mule, "drop_mule"],
            [self.scan_army, "scan_army"],
            [self.scan_location_at_1, "scan_main_base"],
            [self.scan_location_at_2, "scan_2nd"],
            [self.scan_location_at_3, "scan_3rd"],
            [self.scan_location_at_4, "scan_4th"],
            [self.scan_location_at_5, "scan_5th"],
            [self.scan_location_at_6, "scan_6th"],
            [self.scan_location_at_7, "scan_7th"],
            [self.scan_location_at_8, "scan_8th"],
            [self.scan_location_at_9, "scan_9th"],
            [self.scan_location_at_10, "scan_10th"],
            [self.scan_location_at_11, "scan_11th"],
            [self.scan_location_at_12, "scan_12th"],
            [self.scan_location_at_13, "scan_13th"],
            [self.scan_location_at_14, "scan_14th"],
            [self.noop, "don't use ability"],
        ]

        self.army_commands = [
            [self.stim_army, "stim_army"],
            [self.siege_tanks, "siege_tanks"],
            [self.attack_enemy_units, "attack_enemy_units"],
            [self.attack_enemy_structures, "attack_enemy_structures"],
            [self.gather_units_at_1, "gather all units on main base"],
            [self.gather_units_at_2, "gather all units on 3rd"],
            [self.gather_units_at_3, "gather all units on 2nd"],
            [self.gather_units_at_4, "gather all units on a base"],
            [self.gather_units_at_5, "gather all units on a base"],
            [self.gather_units_at_6, "gather all units on a base"],
            [self.gather_units_at_7, "gather all units on a base"],
            [self.gather_units_at_8, "gather all units on a base"],
            [self.gather_units_at_9, "gather all units on a base"],
            [self.gather_units_at_10, "gather all units on a base"],
            [self.gather_units_at_11, "gather all units on a base"],
            [self.gather_units_at_12, "gather all units on a base"],
            [self.gather_units_at_13, "gather all units on a base"],
            [self.gather_units_at_14, "gather all units on a base"],
            [self.hold_position_all_army, "hold_position_all_army"],
            [self.noop, "don't give an order to the army"],
        ]

    async def initialize_location_list(self, locations_sorted):
        self.locations_sorted = locations_sorted

    async def random_strategize(self):
        """
        The main method of the strategy class, handles the decision-making of the model.
        chooses randomly with uniform distribution among the strategies in self.actions_list

        :return:
        The action that was taken in this iteration and the immediate reward associated with the
        execution of that action.
        """
        build_action = random.randint(0, len(self.build_actions) - 1)
        manufacture_unit_action = random.randint(0, len(self.manufacture_unit_actions) - 1)
        research_upgrade_action = random.randint(0, len(self.research_upgrade_actions) - 1)
        command_center_ability = random.randint(0, len(self.command_center_abilities) - 1)
        army_command = random.randint(0, len(self.army_commands) - 1)
        await self.strategize([build_action, manufacture_unit_action, research_upgrade_action, command_center_ability, army_command])

    @staticmethod
    async def execute_command(command):
        await command()

    async def strategize(self, actions: list[int]):
        """
        The main method of the strategy class, handles the action execution as dictated by the model.
        """
        async with asyncio.TaskGroup() as tg:
            reward1 = tg.create_task(self.build_actions[actions[0]][0]())
            reward2 = tg.create_task(self.manufacture_unit_actions[actions[1]][0]())
            reward3 = tg.create_task(self.research_upgrade_actions[actions[2]][0]())
            reward4 = tg.create_task(self.command_center_abilities[actions[3]][0]())
            reward5 = tg.create_task(self.army_commands[actions[4]][0]())

        return reward1.result() + reward2.result() + reward3.result() + reward4.result() + reward5.result()

    async def noop(self):
        return GB.VALID_COMMAND_REWARD

    async def expand_now(self):
        if await self.agent.get_next_expansion():
            await self.agent.expand_now()
            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def get_position_for_depot(self):
        """
        Return a position to build a supply depot at, if position is at first base build behind
        the mineral line

        :return: Point2 for supply depot placement
        """
        if self.agent.townhalls:
            townhall_pos = self.agent.townhalls.random.position
            if townhall_pos == self.agent.start_location.position:
                minerals = self.agent.mineral_field.closer_than(GB.MINERAL_CLOSER_THAN_DISTANCE,
                                                                self.agent.start_location)
                if minerals:
                    return self.agent.start_location.towards_with_random_angle(minerals.random.position,
                                                                               random.randrange(
                                                                                   GB.RANDOM_BEHIND_MINERALS_RANGE_MIN,
                                                                                   GB.RANDOM_BEHIND_MINERALS_RANGE_MAX))
            return await self.get_position_towards_enemy_from_place(townhall_pos)

        return self.agent.start_location.towards_with_random_angle(self.agent.enemy_start_locations[0],
                                                                   random.randrange(
                                                                       GB.RANDOM_BEHIND_MINERALS_RANGE_MIN,
                                                                       GB.RANDOM_BEHIND_MINERALS_RANGE_MAX))

    async def get_position_towards_enemy_from_place(self, place):
        """
        A method that returns a position that is from place towards enemy start location

        :param place: the position from which to calculate the return value
        :return: the position towards the enemy start location
        """
        return place.towards_with_random_angle(
            self.agent.enemy_start_locations[0], random.randrange(GB.RANDOM_BUILDING_RANGE_MIN,
                                                                  GB.RANDOM_BUILDING_RANGE_MAX), GB.RANDOM_ANGLE_LIMIT)

    async def get_position_for_building(self):
        """
        a method that generates a random position to build a structure at

        :return: Point2 for building placement
        """
        if self.agent.townhalls:
            return await self.get_position_towards_enemy_from_place(self.agent.townhalls.random.position)
        else:
            return await self.get_position_towards_enemy_from_place(self.agent.start_location.position)

    def create_build_structure(self, building_uid, add_on=False):
        """
        A method that replaces the Bot_AI.build method, this method is a bit more efficient,
        helps reduce clatter at first base and if add_on is true will make sure the building
        is built with room for the add_on.
        If position isn't valid the function will try again for NUM_OF_RETRIES times.

        :param building_uid: the type of building we try to build
        :param add_on: does the building specified by building_uid needs space for an add_on
        """
        async def inner():
            if not self.agent.can_afford(building_uid) or (building_uid == UId.ENGINEERINGBAY and self.agent.structures(UId.ENGINEERINGBAY).amount >= GB.MAX_AMOUNT_ENGIBAYS):
                return GB.INVALID_COMMAND_REWARD

            for i in range(GB.NUM_OF_RETRIES):
                if building_uid == UId.SUPPLYDEPOT:
                    pos = await self.get_position_for_depot()
                    if not await self.check_building_position_radius(pos, GB.DEPO_RADIUS):
                        continue
                else:
                    if add_on:
                        addon_size = GB.DEPO_RADIUS
                    else:
                        addon_size = 0
                    pos = await self.get_position_for_building()
                    if not await self.check_building_position_radius(pos, GB.BUILDING_RADIUS + addon_size):
                        continue

                if not await self.agent.can_place_single(building_uid, pos):
                    continue

                if add_on:
                    if not await self.agent.can_place_single(UId.SUPPLYDEPOT, pos.offset((2.5, -0.5))):
                        continue

                builder = self.agent.select_build_worker(pos)

                if builder is not None:
                    self.agent.do(builder.build(building_uid, pos))
                    return GB.GOOD_COMMAND_REWARD

            return GB.VALID_COMMAND_REWARD

        return inner

    async def check_building_position_radius(self, position, radius):
        if self.agent.structures.closer_than(radius + GB.STRUCTURES_SAFE_RADIUS, position).exists:
            return False
        return True


    async def build_refinery(self):
        """
        A method that builds a Refinery on a vespene gas near a random CommandCenter if
        we can afford one and if we have any CommandCenters.

        :return: Reward of action depending on it's success
        """
        if self.agent.can_afford(UId.REFINERY) and self.agent.townhalls:
            vespenes = self.agent.vespene_geyser.closer_than(GB.MINERAL_CLOSER_THAN_DISTANCE,
                                                             self.agent.townhalls.random)

            if vespenes:
                await self.agent.build(UId.REFINERY, vespenes.random)
                return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD


    async def build_worker(self):
        """
        A method that transforms an idle CommandCenter into an Orbital Command if it can afford to do so,
        or if said CommandCenter is already an orbital command then this method will build an SCV if
        it can afford to do so.

        :return: Reward of action depending on it's success
        """
        if self.agent.townhalls.idle:
            for town_hall in self.agent.townhalls.idle:
                if self.agent.can_afford(UId.SCV):
                    town_hall.train(UId.SCV, queue=True)
                    return GB.GOOD_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def upgrade_to_orbital(self):
        if self.agent.townhalls.idle:
            for town_hall in self.agent.townhalls.idle:
                if town_hall.type_id == UId.COMMANDCENTER \
                        and self.agent.can_afford(UId.ORBITALCOMMAND, check_supply_cost=False):
                    self.agent.do(town_hall(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND))
                    return GB.VALID_COMMAND_REWARD
        return GB.INVALID_COMMAND_REWARD

    async def drop_mule(self):
        """
        A method that drops a mule at the location of a random orbital command that has enough
        energy to cast the calldown mule ability if the agent has such orbital command.

        :return: Reward of action depending on it's success
        """
        for town_hall in self.agent.townhalls:
            if town_hall.type_id == UId.ORBITALCOMMAND and town_hall.energy >= GB.ENERGY_FOR_MULE_OR_SCAN:
                self.agent.do(town_hall(AbilityId.CALLDOWNMULE_CALLDOWNMULE,
                                        self.agent.mineral_field.closest_to(town_hall)))
                return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def scan_army(self):
        """
        A method that uses the scanner_sweep ability at the location of a random army unit using
        a random orbital command that has enough energy to cast the ability if the agent has such orbital command.

        :return: Reward of action depending on it's success
        """
        for town_hall in self.agent.townhalls:
            if town_hall.type_id == UId.ORBITALCOMMAND and town_hall.energy >= GB.ENERGY_FOR_MULE_OR_SCAN:
                if self.agent.units(UId.MARINE):
                    unit = UId.MARINE
                elif self.agent.units(UId.MARAUDER):
                    unit = UId.MARAUDER
                elif self.agent.units(UId.SIEGETANK):
                    unit = UId.SIEGETANK

                else:
                    return GB.INVALID_COMMAND_REWARD

                self.agent.do(town_hall(AbilityId.SCANNERSWEEP_SCAN,
                                        self.agent.units(unit).random.position))
                return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    def scan_location(self, location):
        """
        A method that uses the scanner_sweep ability on a location using
        a random orbital command that has enough energy to cast the ability if the agent has such orbital command.

        :param: location: the location we want to scan
        :return: Reward of action depending on it's success
        """
        for town_hall in self.agent.townhalls:
            if town_hall.type_id == UId.ORBITALCOMMAND and town_hall.energy >= GB.ENERGY_FOR_MULE_OR_SCAN:

                self.agent.do(town_hall(AbilityId.SCANNERSWEEP_SCAN, location))
                return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD


    def create_build_unit_from_structure(self, uid_building, uid_unit):
        async def inner():
            if not self.agent.can_afford(uid_unit):
                return GB.INVALID_COMMAND_REWARD

            ready_structures = self.agent.structures(uid_building).ready
            if ready_structures:
                idle_structures = ready_structures.idle
                if idle_structures:
                    structure = idle_structures.random
                    structure.train(uid_unit, queue=True)
                    return GB.GOOD_COMMAND_REWARD

            return GB.INVALID_COMMAND_REWARD

        return inner


    def create_build_addon(self, addon_uid: UId, structure_uid: UId, create_addon_ability: AbilityId):
        """
        A method that handles building addons on barracks

        :param addon_uid: the uid of the addon we want to build
        :param structure_uid the uid of the structure on which we want to build an addon
        :param create_addon_ability: the Abilityid of the ability used to build the addon specified of uid
        :return: Reward of action depending on it's success
        """
        async def inner():
            if not self.agent.can_afford(addon_uid):
                return GB.INVALID_COMMAND_REWARD

            ready_uid_structures = self.agent.structures(structure_uid).ready
            if ready_uid_structures:
                idle_uid_structures = ready_uid_structures.idle
                if idle_uid_structures:
                    structure_without_addon = None
                    for structure in idle_uid_structures:
                        if not structure.has_add_on:
                            structure_without_addon = structure
                            break

                    if structure_without_addon is not None:
                        can_place = await (self.agent.can_place_single(UId.SUPPLYDEPOT, structure_without_addon.add_on_position))

                        if can_place:
                            self.agent.do(structure_without_addon(create_addon_ability))
                            return GB.VALID_COMMAND_REWARD

            return GB.INVALID_COMMAND_REWARD

        return inner

    async def upgrade_ground_weapons(self):
        """
        A method that handles upgrading weapons for infantry

        :return: Reward of action depending on it's success
        """
        return await self.upgrade_ground(UpId.TERRANINFANTRYWEAPONSLEVEL1, UpId.TERRANINFANTRYWEAPONSLEVEL2,
                                         UpId.TERRANINFANTRYWEAPONSLEVEL3)

    async def upgrade_ground_armor(self):
        """
        A method that handles upgrading Armor for infantry

        :return: Reward of action depending on it's success
        """
        return await self.upgrade_ground(UpId.TERRANINFANTRYARMORSLEVEL1, UpId.TERRANINFANTRYARMORSLEVEL2,
                                         UpId.TERRANINFANTRYARMORSLEVEL3)

    async def upgrade_ground(self, upid1, upid2, upid3):
        """
        A method that handles the upgrading chain of Terran infantry upgrades from engineering bays
        note: All params must be of the same upgrade in different levels:
        example:
        UpId.TERRANINFANTRYARMORSLEVEL1, UpId.TERRANINFANTRYARMORSLEVEL2, UpId.TERRANINFANTRYARMORSLEVEL3

        :param upid1: the upgrade uid of a level 1 upgrade
        :param upid2: the upgrade uid of a level 2 upgrade
        :param upid3: the upgrade uid of a level 3 upgrade

        :return: Reward of action depending on it's success
        """
        if not self.agent.already_pending_upgrade(upid1):
            if self.agent.can_afford(upid1):

                engibay = self.agent.structures(UId.ENGINEERINGBAY).idle
                if engibay:
                    engibay.random.research(upid1)
                    return GB.GOOD_COMMAND_REWARD

        elif self.agent.structures(UId.ARMORY).ready \
                and not self.agent.already_pending_upgrade(upid2):
            if self.agent.can_afford(upid2):
                engibay = self.agent.structures(UId.ENGINEERINGBAY).idle
                if engibay:
                    engibay.random.research(upid2)
                    return GB.GOOD_COMMAND_REWARD

        elif not self.agent.already_pending_upgrade(upid3):
            if self.agent.can_afford(upid3):

                engibay = self.agent.structures(UId.ENGINEERINGBAY).idle
                if engibay:
                    engibay.random.research(upid3)
                    return GB.GOOD_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def upgrade_marine(self):
        """
        Handles researching the combat shields upgrade

        :return: Reward of action depending on it's success
        """
        return await self.upgrade_from_barracks_techlab(UpId.SHIELDWALL)

    async def upgrade_bio(self):
        """
        Handles researching the STIMPACK upgrade

        :return: Reward of action depending on it's success
        """
        return await self.upgrade_from_barracks_techlab(UpId.STIMPACK)

    async def upgrade_from_barracks_techlab(self, upid):
        """
        Handles researching upgrades from barracks techlab

        :param upid: the upgrade id of the requested upgrade
        :return: Reward of action depending on it's success
        """
        if self.agent.structures(UId.BARRACKSTECHLAB).idle and self.agent.can_afford(upid):
            self.agent.structures(UId.BARRACKSTECHLAB).idle.random.research(upid)
            return GB.GOOD_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def stim_army(self):
        """
        This method activates the STIM buff on all infantry units
        This buff raises attack and movement speed of units while doing a one time
        single burst of damage.

        :return: Reward of action depending on it's success
        """
        for marine in self.agent.units(UId.MARINE):
            self.agent.do(marine(AbilityId.EFFECT_STIM_MARINE))

        for marauder in self.agent.units(UId.MARAUDER):
            self.agent.do(marauder(AbilityId.EFFECT_STIM_MARINE))

        return GB.VALID_COMMAND_REWARD

    async def siege_tanks(self):
        """
        Handles Siegeing all tanks in army

        :return: Reward of action depending on it's success
        """
        if self.is_sieged:
            ability = AbilityId.UNSIEGE_UNSIEGE
            self.is_sieged = False
            unit = UId.SIEGETANKSIEGED

        else:
            ability = AbilityId.SIEGEMODE_SIEGEMODE
            self.is_sieged = True
            unit = UId.SIEGETANK

        tanks = self.agent.units(unit)
        if tanks.amount > 0:

            for tank in tanks:
                self.agent.do(tank(ability))

            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def attack_enemy_units(self):
        """
        Handles using all units to attack enemy units, notice that medivacs are ordered to follow
        other units to avoid them going in front of the army.

        :return: Reward of action depending on it's success
        """
        if self.agent.enemy_units:
            await self.attack_enemy(self.agent.enemy_units)
            return GB.VALID_COMMAND_REWARD
        else:
            return GB.INVALID_COMMAND_REWARD

    async def attack_enemy_structures(self):
        """
        Handles using all units to attack enemy structures, notice that medivacs are ordered to follow
        other units to avoid them going in front of the army.

        :return: Reward of action depending on it's success
        """
        if self.agent.enemy_structures:
            await self.attack_enemy(self.agent.enemy_structures)
            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def attack_enemy(self, what_to_attack):
        await self.attack_position_with_unit_type(UId.MARINE, what_to_attack)

        await self.attack_position_with_unit_type(UId.MARAUDER, what_to_attack)

        await self.attack_position_with_unit_type(UId.SIEGETANK, what_to_attack)

        await self.attack_position_with_unit_type(UId.THOR, what_to_attack)

        await self.follow_other_unit(UId.MEDIVAC)

    async def attack_enemy_main_one_type(self, uid):
        """
        A method that attacks the main of the enemy with one unit type (meant for internal use)

        :param uid: the uid of the attacking unit type
        """
        for army_unit in self.agent.units(uid):
            army_unit.attack(self.agent.enemy_start_locations[0])


    async def gather_units_at(self, location):
        """
        A method for internal use the gathers all army units at location specified by location param

        :param location: the location units will move to
        """
        await self.gather_one_type_at_location(UId.MARINE, location)

        await self.gather_one_type_at_location(UId.MARAUDER, location)

        await self.gather_one_type_at_location(UId.SIEGETANK, location)

        await self.gather_one_type_at_location(UId.THOR, location)

        await self.follow_other_unit(UId.MEDIVAC)

    async def gather_units_at_1(self):
        await self.gather_units_at(self.locations_sorted[0])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_2(self):
        await self.gather_units_at(self.locations_sorted[1])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_3(self):
        await self.gather_units_at(self.locations_sorted[2])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_4(self):
        await self.gather_units_at(self.locations_sorted[3])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_5(self):
        await self.gather_units_at(self.locations_sorted[4])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_6(self):
        await self.gather_units_at(self.locations_sorted[5])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_7(self):
        await self.gather_units_at(self.locations_sorted[6])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_8(self):
        await self.gather_units_at(self.locations_sorted[7])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_9(self):
        await self.gather_units_at(self.locations_sorted[8])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_10(self):
        await self.gather_units_at(self.locations_sorted[9])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_11(self):
        await self.gather_units_at(self.locations_sorted[10])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_12(self):
        await self.gather_units_at(self.locations_sorted[11])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_13(self):
        await self.gather_units_at(self.locations_sorted[12])
        return GB.VALID_COMMAND_REWARD

    async def gather_units_at_14(self):
        await self.gather_units_at(self.locations_sorted[13])
        return GB.VALID_COMMAND_REWARD

    async def scan_location_at_1(self):
        return self.scan_location(self.locations_sorted[0])

    async def scan_location_at_2(self):
        return self.scan_location(self.locations_sorted[1])

    async def scan_location_at_3(self):
        return self.scan_location(self.locations_sorted[2])

    async def scan_location_at_4(self):
        return self.scan_location(self.locations_sorted[3])

    async def scan_location_at_5(self):
        return self.scan_location(self.locations_sorted[4])

    async def scan_location_at_6(self):
        return self.scan_location(self.locations_sorted[5])

    async def scan_location_at_7(self):
        return self.scan_location(self.locations_sorted[6])

    async def scan_location_at_8(self):
        return self.scan_location(self.locations_sorted[7])

    async def scan_location_at_9(self):
        return self.scan_location(self.locations_sorted[8])

    async def scan_location_at_10(self):
        return self.scan_location(self.locations_sorted[9])

    async def scan_location_at_11(self):
        return self.scan_location(self.locations_sorted[10])

    async def scan_location_at_12(self):
        return self.scan_location(self.locations_sorted[11])

    async def scan_location_at_13(self):
        return self.scan_location(self.locations_sorted[12])

    async def scan_location_at_14(self):
        return self.scan_location(self.locations_sorted[13])

    async def gather_one_type_at_location(self, uid, location):
        """
        A method that sends ally unit of one type to the closest ally base to enemy main base
        (meant for internal use)

        :param location: the location to move
        :param uid: the uid of the ally unit type
        """
        for army_unit in self.agent.units(uid):
            army_unit.move(location)

    async def attack_position_with_unit_type(self, uid, to_attack):
        """
        A method that attacks a position or an enemy with one unit type (meant for internal use)

        :param uid: unit type uid to send for attack
        :param to_attack: the position or enemy to attack
        """
        for unit in self.agent.units(uid):
            unit.attack(to_attack.closest_to(unit))

    async def hold_position_all_army(self):
        """
        A method that sends the hold position order to the entire army

        :return: Reward of action depending on it's success
        """
        await self.hold_position_one_unit_type(UId.MARINE)

        await self.hold_position_one_unit_type(UId.MARAUDER)

        await self.hold_position_one_unit_type(UId.SIEGETANK)

        await self.hold_position_one_unit_type(UId.THOR)

        return GB.VALID_COMMAND_REWARD

    async def hold_position_one_unit_type(self, uid):
        """
        Order all units from unit type specified by uid param to hold position

        :param uid: the unit type to hold position
        """
        for unit in self.agent.units(uid):
            unit.hold_position()

    async def follow_other_unit(self, follower):
        """
        A method the sends one unit type to follow a random ally unit

        :param follower: the unit type that will follow
        """
        if self.agent.units(UId.MARAUDER):
            await self.all_medivacs_follow(UId.MARAUDER, follower)

        elif self.agent.units(UId.MARINE):
            await self.all_medivacs_follow(UId.MARINE, follower)

    async def all_medivacs_follow(self, uid_to_follow, follower):
        """
        A method that sends all medivacs to follow the unit specified by uid_to_follow

        :param uid_to_follow: the unit uid to follow
        :param follower: the unit uid that follows
        """
        for follower in self.agent.units(follower):
            follower.move(self.agent.units(uid_to_follow).closest_to(follower.position))
