import numpy as np
from sc2.ids.unit_typeid import UnitTypeId as UId
from math import pi

GAME_TIME_LIMIT = 1200

total_steps = 100000

START_ITERATION = 1

# Constants for Rewards.py
STARTING_WORKER_AMOUNT = 12
UNIT_REWARD_MODIFIER = 0.1
UNIT_UPGRADE_REWARD_MODIFIER = 0.17
UNIT_IS_ATTACKING_REWARD_MODIFIER = 0.1
ENEMY_UNIT_KILLED_REWARD_MODIFIER = UNIT_REWARD_MODIFIER
ALLY_UNIT_KILLED_REWARD_MODIFIER = UNIT_REWARD_MODIFIER
MAX_AMOUNT_ENGIBAYS = 2
step_punishment = np.logspace(1, 0, total_steps) / 10

# constants for Terran_Strategy
STRUCTURES_SAFE_RADIUS = 2
RANDOM_BUILDING_RANGE_MIN = 4
RANDOM_BUILDING_RANGE_MAX = 18
DEPO_RADIUS = 2
BUILDING_RADIUS = 3
RANDOM_ANGLE_LIMIT = pi / 4
INVALID_COMMAND_REWARD = -0.1
VALID_COMMAND_REWARD = 0
VALID_CREATE_UNIT_COMMAND_REWARD_MOD = 0.01
ENERGY_FOR_MULE_OR_SCAN = 50
RANDOM_BEHIND_MINERALS_RANGE_MIN = 8
RANDOM_BEHIND_MINERALS_RANGE_MAX = 16
PLACEMENT_STEP = 4
NUM_OF_RETRIES = 100
DISTANCE_FROM_RAMP_RALLY_POINT = 20
MINERAL_CLOSER_THAN_DISTANCE = 15

# constants for stable-baselines3 use
OBSERVATION_SPACE_SHAPE_MAP = (200, 176, 3)
ACTION_SPACE_SIZE = [17, 8, 5, 17, 20]
OBSERVATION_SPACE_SHAPE_INFO = (70 + sum(ACTION_SPACE_SIZE) * 2,)
LOW_BOUND = -np.inf
HIGH_BOUND = np.inf

# constants for feature extractor
MINIMAL_ENERGY = 50
MEMORY_SIZE = 1000
RADIUS_FROM_LOCATION = 30

protoss_units_list = [UId.PROBE, UId.ZEALOT, UId.STALKER, UId.ORACLE, UId.ARCHON, UId.CARRIER, UId.COLOSSUS,
                      UId.DARKTEMPLAR, UId.HIGHTEMPLAR, UId.IMMORTAL, UId.MOTHERSHIP, UId.OBSERVER,
                      UId.PHOENIX, UId.SENTRY, UId.VOIDRAY, UId.WARPPRISM, UId.TEMPEST, UId.ADEPT, UId.DISRUPTOR]

protoss_structures_list = [UId.ASSIMILATOR, UId.CYBERNETICSCORE, UId.DARKSHRINE, UId.FLEETBEACON, UId.FORGE,
                           UId.GATEWAY, UId.WARPGATE, UId.NEXUS, UId.PHOTONCANNON, UId.PYLON, UId.ROBOTICSBAY,
                           UId.ROBOTICSFACILITY, UId.STARGATE, UId.TEMPLARARCHIVE,
                           UId.TWILIGHTCOUNCIL, UId.WARPGATE, UId.SHIELDBATTERY]

terran_unit_list = [UId.SCV, UId.MARINE, UId.SIEGETANK, UId.SIEGETANKSIEGED, UId.MEDIVAC, UId.MARAUDER, UId.THOR, UId.BATTLECRUISER]

terran_structures_list = [UId.COMMANDCENTER, UId.ORBITALCOMMAND, UId.SUPPLYDEPOTLOWERED,
                          UId.SUPPLYDEPOT, UId.BARRACKS, UId.FACTORY, UId.STARPORT,
                          UId.ENGINEERINGBAY, UId.ARMORY, UId.REFINERY, UId.FUSIONCORE]

# COLORS
MINERAL_COLOR = [175, 255, 255]
VESPENE_COLOR = [255, 175, 255]
ENEMY_UNIT_COLOR = [100, 0, 255]
ENEMY_STRUCTURE_COLOR = [0, 100, 255]
ALLY_STRUCTURE_COLOR = [0, 255, 175]
ALLY_BASE_COLOR = [255, 255, 175]
MARINE_COLOR = [255, 75, 75]
SCV_COLOR = [175, 255, 0]
