import numpy as np
from sc2.ids.unit_typeid import UnitTypeId as UId
from math import pi

GAME_TIME_LIMIT = 1200

total_steps = 10000

START_ITERATION = 1

# Constants for Rewards.py
STARTING_WORKER_AMOUNT = 12
UNIT_REWARD_MODIFIER = 0.001
ATTACK_BONUS = 0.015
BUILD_UNIT_BONUS = 0.01
BUILD_STRUCTURES_BONUS = 0.05
HARVEST_BONUS = 0.05
ENEMY_UNIT_KILLED_REWARD_MODIFIER = 0.001
ALLY_UNIT_KILLED_PUNISHMENT_MODIFIER = 0.0005
ACCESS_MINERALS_FOR_PUNISHMENT = 1000
ACCESS_GAS_FOR_PUNISHMENT = 500
PUNISHMENT_FOR_NOT_SPENDING = 0.01
END_GAME_PUN_REWARD = 0.02
steps_for_pun = np.linspace(0, 1, total_steps)
step_punishment = ((np.exp(steps_for_pun ** 3) / 10) - 0.1) * 10

# constants for Terran_Strategy
STRUCTURES_SAFE_RADIUS = 2
RANDOM_BUILDING_RANGE_MIN = 4
RANDOM_BUILDING_RANGE_MAX = 18
DEPO_RADIUS = 2
BUILDING_RADIUS = 3
RANDOM_ANGLE_LIMIT = pi / 4
INVALID_COMMAND_REWARD = -0.0001
VALID_COMMAND_REWARD = 0
ENERGY_FOR_MULE_OR_SCAN = 50
RANDOM_BEHIND_MINERALS_RANGE_MIN = 8
RANDOM_BEHIND_MINERALS_RANGE_MAX = 16
PLACEMENT_STEP = 4
NUM_OF_RETRIES = 100
DISTANCE_FROM_RAMP_RALLY_POINT = 20
MINERAL_CLOSER_THAN_DISTANCE = 15

# constants for stable-baselines3 use
OBSERVATION_SPACE_SHAPE = (142,)
ACTION_SPACE_SIZE = 55
LOW_BOUND = np.NINF
HIGH_BOUND = np.Inf

# constant for Data_Scraper.py
DATA_DIR = "Data"

# constants for feature extractor
MINIMAL_ENERGY = 50
MEMORY_SIZE = 20
RADIUS_FROM_LOCATION = 30

protoss_units_list = [UId.PROBE, UId.ZEALOT, UId.STALKER, UId.ORACLE, UId.ARCHON, UId.CARRIER, UId.COLOSSUS,
                      UId.DARKTEMPLAR, UId.HIGHTEMPLAR, UId.IMMORTAL, UId.MOTHERSHIP, UId.OBSERVER,
                      UId.PHOENIX, UId.SENTRY, UId.VOIDRAY, UId.WARPPRISM, UId.TEMPEST, UId.ADEPT, UId.DISRUPTOR]

protoss_structures_list = [UId.ASSIMILATOR, UId.CYBERNETICSCORE, UId.DARKSHRINE, UId.FLEETBEACON, UId.FORGE,
                           UId.GATEWAY, UId.WARPGATE, UId.NEXUS, UId.PHOTONCANNON, UId.PYLON, UId.ROBOTICSBAY,
                           UId.ROBOTICSFACILITY, UId.STARGATE, UId.TEMPLARARCHIVE,
                           UId.TWILIGHTCOUNCIL, UId.WARPGATE, UId.SHIELDBATTERY]

terran_unit_list = [UId.SCV, UId.MARINE, UId.SIEGETANK, UId.SIEGETANKSIEGED, UId.MEDIVAC, UId.MARAUDER]

terran_structures_list = [UId.COMMANDCENTER, UId.ORBITALCOMMAND, UId.SUPPLYDEPOTLOWERED,
                          UId.SUPPLYDEPOT, UId.BARRACKS, UId.FACTORY, UId.STARPORT,
                          UId.ENGINEERINGBAY, UId.ARMORY]
