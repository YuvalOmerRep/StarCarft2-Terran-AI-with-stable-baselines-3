import random

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId as UId
from sc2.ids.upgrade_id import UpgradeId as UpId
from sc2.unit import AbilityId
import common as GB


class Terran_Strategy:
    def __init__(self, agent: BotAI):
        self.agent = agent

    async def strategize(self):
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

        self.actions_list = [
            [self.build_from_command_center, "build_from_command_center"],
            [self.expand_now, "expand_now"],
            [self.build_refinery, "build_refinery"],
            [self.build_supply_depo, "build_supply_depo"],
            [self.build_factory, "build_factory"],
            [self.build_barracks, "build_barracks"],
            [self.build_engineeringbay, "build_engineeringbay"],
            [self.build_marine, "build_marine"],
            [self.build_marauder, "build_marauder"],
            [self.build_tank, "build_tank"],
            [self.build_thor, "build_thor"],
            [self.build_reactor, "build_reactor"],
            [self.build_techlab, "build_techlab"],
            [self.build_armory, "build_armory"],
            [self.upgrade_ground_weapons, "upgrade_ground_weapons"],
            [self.upgrade_ground_armor, "upgrade_ground_armor"],
            [self.build_starport, "build_starport"],
            [self.build_from_starport, "build_from_starport"],
            [self.upgrade_bio, "upgrade_bio"],
            [self.upgrade_marine, "upgrade_marine"],
            [self.stim_army, "stim_army"],
            [self.siege_tanks, "siege_tanks"],
            # [self.attack_enemy_main, "attack_enemy_main"],
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
            # [self.gather_units_at_outpost, "gather_units_at_outpost"],
            # [self.gather_units_in_front_of_third, "gather_units_in_front_of_third"],
            [self.hold_position_all_army, "hold_position_all_army"],
            [self.drop_mule, "drop_mule"],
            [self.scan_army, "scan_army"],
            [self.scan_location_at_1, "scan main base"],
            [self.scan_location_at_2, "scan 2nd"],
            [self.scan_location_at_3, "scan 3rd"],
            [self.scan_location_at_4, "scan a base location"],
            [self.scan_location_at_5, "scan a base location"],
            [self.scan_location_at_6, "scan a base location"],
            [self.scan_location_at_7, "scan a base location"],
            [self.scan_location_at_8, "scan a base location"],
            [self.scan_location_at_9, "scan a base location"],
            [self.scan_location_at_10, "scan a base location"],
            [self.scan_location_at_11, "scan a base location"],
            [self.scan_location_at_12, "scan a base location"],
            [self.scan_location_at_13, "scan a base location"],
            [self.scan_location_at_14, "scan a base location"],
        ]

    async def initialize_location_list(self, locations_sorted):
        self.locations_sorted = locations_sorted

    async def strategize(self):
        """
        The main method of the strategy class, handles the decision making of the model.
        chooses randomly with uniform distribution among the strategies in self.actions_list

        :return:
        The action that was taken in this iteration and the immediate reward associated with the
        execution of that action.
        """
        action = random.choice(self.actions_list)

        reward = await action[0]()

        return action[1], reward

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

    async def build(self, building_uid, add_on=False):
        """
        A method that replaces the Bot_AI.build method, this method is a bit more efficient,
        helps reduce clatter at first base and if add_on is true will make sure the building
        is built with room for the add_on.
        If position isn't valid the function will try again for NUM_OF_RETRIES times.

        :param building_uid: the type of building we try to build
        :param add_on: does the building specified by building_uid needs space for an add_on
        """
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

    async def check_building_position_radius(self, position, radius):
        if self.agent.structures.closer_than(radius + GB.STRUCTURES_SAFE_RADIUS, position).exists:
            return False
        return True

    async def build_supply_depo(self):
        """
        A method that builds a supply depo at a random location if we can afford
        building one.

        :return: Reward of action depending on it's success
        """
        if self.agent.can_afford(UId.SUPPLYDEPOT):
            await self.build(UId.SUPPLYDEPOT)

            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_factory(self):
        """
        A method that builds a factory depo at a random location if we can afford
        building one.

        :return: Reward of action depending on it's success
        """
        if self.agent.can_afford(UId.FACTORY):
            await self.build(UId.FACTORY, add_on=True)

            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_starport(self):
        """
        A method that builds a starport at a random location if we can afford
        building one.

        :return: Reward of action depending on it's success
        """
        if self.agent.can_afford(UId.STARPORT):
            await self.build(UId.STARPORT, add_on=True)
            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_barracks(self):
        """
        A method that builds a barracks at a random location if we can afford
        building one.

        :return: Reward of action depending on it's success
        """
        if self.agent.can_afford(UId.BARRACKS):
            await self.build(UId.BARRACKS, add_on=True)

            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

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

    async def build_engineeringbay(self):
        """
        A method that builds an Engineering Bay at a random location if we can afford
        building one.

        :return: Reward of action depending on it's success
        """
        if self.agent.can_afford(UId.ENGINEERINGBAY):
            await self.build(UId.ENGINEERINGBAY)

            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_armory(self):
        """
        A method that builds an armory at a random location if we can afford
        building one.

        :return: Reward of action depending on it's success
        """
        if self.agent.can_afford(UId.ARMORY) and not self.agent.already_pending(UId.ARMORY):
            await self.build(UId.ARMORY)

            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_from_command_center(self):
        """
        A method that transforms an idle CommandCenter into an Orbital Command if it can afford to do so,
        or if said CommandCenter is already an orbital command then this method will build a SCV if
        it can afford to do so.

        :return: Reward of action depending on it's success
        """
        if self.agent.townhalls.idle:
            for town_hall in self.agent.townhalls.idle:
                if town_hall.type_id == UId.COMMANDCENTER \
                        and self.agent.can_afford(UId.ORBITALCOMMAND, check_supply_cost=False):
                    self.agent.do(town_hall(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND))
                    return GB.VALID_COMMAND_REWARD

                elif self.agent.can_afford(UId.SCV):
                    town_hall.train(UId.SCV, queue=True)
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

    async def build_marine(self):
        """
        A method that builds a marine, this method will build that marine from a random barrack with the following
        priorities:
        1) an idle barracks with a reactor
        2) a non idle barracks with a reactor
        3) a random ready barracks

        :return: Reward of action depending on it's success
        """
        structure_ready = self.agent.structures(UId.BARRACKS).ready

        if self.agent.can_afford(UId.MARINE) and structure_ready:
            structure_idle = structure_ready.idle

            if structure_idle:
                if await find_from_group_with_reactor(structure_idle, UId.MARINE):
                    return GB.VALID_COMMAND_REWARD

            if await find_from_group_with_reactor(structure_ready, UId.MARINE):
                return GB.VALID_COMMAND_REWARD

            if structure_idle:
                structure_idle.random.train(UId.MARINE, queue=True)
            else:
                structure_ready.random.train(UId.MARINE, queue=True)

            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_marauder(self):
        """
        A method that builds a marauder from a random idle barracks with a techlab

        :return: Reward of action depending on it's success
        """
        barracks_ready = self.agent.structures(UId.BARRACKS).ready
        if barracks_ready:
            barracks_idle = barracks_ready.idle

            if barracks_idle:
                for barrack in barracks_idle:
                    if barrack.has_techlab:
                        if self.agent.can_afford(UId.MARAUDER):
                            barrack.train(UId.MARAUDER, queue=True)
                            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_reactor(self):
        """
        A method that builds a reactor on a random idle barracks that doesn't have
        and addon

        :return: Reward of action depending on it's success
        """
        if await self.build_addon(UId.REACTOR, AbilityId.BUILD_REACTOR_BARRACKS):
            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_techlab(self):
        """
        A method that builds a techlab on a random idle barracks that doesn't have
        and addon

        :return: Reward of action depending on it's success
        """
        if await self.build_addon(UId.TECHLAB, AbilityId.BUILD_TECHLAB_BARRACKS):
            return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_from_factory(self, uid):
        """
        A method that builds a techlab or a tank from a random idle factory

        :param uid: the unit type to build for the factory
        :return: Reward of action depending on it's success
        """
        return await self.build_from_factory_or_starport(UId.FACTORY, uid, UId.FACTORYTECHLAB,
                                                         AbilityId.BUILD_TECHLAB_FACTORY)

    async def build_from_starport(self):
        """
        A method that builds a reactor or a medivac from a random idle starport

        :return: Reward of action depending on it's success
        """
        return await self.build_from_factory_or_starport(UId.STARPORT, UId.MEDIVAC,
                                                         UId.STARPORTREACTOR, AbilityId.BUILD_REACTOR_STARPORT)

    async def build_from_factory_or_starport(self, uid_building, uid_unit, uid_add_on, ability):
        """
        a method that handles building from factories and starport

        :param uid_building: the uid of a structure type we want to build from
        :param uid_unit: the uid of a unit type we want to build
        :param uid_add_on: the uid of the addon we want on the structure type
        :param ability: the ability used to build the addon
        :return: Reward of action depending on it's success
        """
        ready_structures = self.agent.structures(uid_building).ready
        idle_structures = ready_structures.idle
        if ready_structures:
            if idle_structures:
                structure = idle_structures.random
                if structure.has_add_on:
                    if self.agent.can_afford(uid_unit):
                        structure.train(uid_unit, queue=True)
                        return GB.VALID_COMMAND_REWARD

                elif self.agent.can_afford(uid_add_on):
                    can_place = await (self.agent.can_place_single(UId.SUPPLYDEPOT,
                                                                   structure.add_on_position))

                    if can_place:
                        self.agent.do(structure(ability))
                        return GB.VALID_COMMAND_REWARD

            for building in ready_structures:
                if building.has_add_on:
                    if self.agent.can_afford(uid_unit):
                        building.train(uid_unit, queue=True)
                        return GB.VALID_COMMAND_REWARD

                elif self.agent.can_afford(uid_add_on):
                    can_place = await (self.agent.can_place_single(UId.SUPPLYDEPOT,
                                                                   building.add_on_position))

                    if can_place:
                        self.agent.do(building(ability))
                        return GB.VALID_COMMAND_REWARD

        return GB.INVALID_COMMAND_REWARD

    async def build_thor(self):
        """
        A method that builds a thor or a techlab on a random factory

        :return: Reward of action depending on it's success
        """
        return await self.build_from_factory(UId.THOR)

    async def build_tank(self):
        """
        A method that builds a tank or a techlab on a random factory

        :return: Reward of action depending on it's success
        """
        return await self.build_from_factory(UId.SIEGETANK)

    async def build_addon(self, uid, ability):
        """
        A method that handles building addons on barracks

        :param uid: the uid of the addon we want to build
        :param ability: the Abilityid of the ability used to build the addon specified of uid
        :return: Reward of action depending on it's success
        """
        barracks_ready = self.agent.structures(UId.BARRACKS).ready
        if self.agent.can_afford(uid) and barracks_ready:
            barracks_idle = barracks_ready.idle
            if barracks_idle:
                barrack = None
                for barrack_idle in barracks_idle:
                    if not barrack_idle.has_add_on:
                        barrack = barrack_idle
                        break

                if barrack is not None:
                    can_place = await (self.agent.can_place_single(UId.SUPPLYDEPOT, barrack.add_on_position))

                    if can_place:
                        self.agent.do(barrack(ability))
                        return 1

        return 0

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
                    return GB.VALID_COMMAND_REWARD

        elif self.agent.structures(UId.ARMORY).ready \
                and not self.agent.already_pending_upgrade(upid2):
            if self.agent.can_afford(upid2):
                engibay = self.agent.structures(UId.ENGINEERINGBAY).idle
                if engibay:
                    engibay.random.research(upid2)
                    return GB.VALID_COMMAND_REWARD

        elif not self.agent.already_pending_upgrade(upid3):
            if self.agent.can_afford(upid3):

                engibay = self.agent.structures(UId.ENGINEERINGBAY).idle
                if engibay:
                    engibay.random.research(upid3)
                    return GB.VALID_COMMAND_REWARD

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
            return GB.VALID_COMMAND_REWARD

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

    async def attack_enemy_main(self):
        """
        Handles using all units to attack enemy main base, notice that medivacs are ordered to follow
        other units to avoid them going in front of the army.

        :return: Reward of action depending on it's success
        """
        await self.attack_enemy_main_one_type(UId.MARINE)

        await self.attack_enemy_main_one_type(UId.MARAUDER)

        await self.attack_enemy_main_one_type(UId.SIEGETANK)

        await self.attack_enemy_main_one_type(UId.THOR)

        await self.follow_other_unit(UId.MEDIVAC)

        return GB.VALID_COMMAND_REWARD

    async def attack_enemy_main_one_type(self, uid):
        """
        A method that attacks the main of the enemy with one unit type (meant for internal use)

        :param uid: the uid of the attacking unit type
        """
        for army_unit in self.agent.units(uid):
            army_unit.attack(self.agent.enemy_start_locations[0])

    async def gather_units_at_outpost(self):
        """
        A method that sends ally army to the closest ally base to enemy main base

        :return: Reward of action depending on it's success
        """
        if self.agent.townhalls:
            await self.gather_units_at(self.agent.townhalls.closest_to(self.agent.enemy_start_locations[0]))

        return GB.VALID_COMMAND_REWARD

    async def gather_units_in_front_of_third(self):
        """
        A method that sends ally army to a position between second and third base

        :return: Reward of action depending on it's success
        """
        await self.gather_units_at(
            self.agent.main_base_ramp.bottom_center.towards(self.agent.enemy_start_locations[0],
                                                            GB.DISTANCE_FROM_RAMP_RALLY_POINT))

        return GB.VALID_COMMAND_REWARD

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
