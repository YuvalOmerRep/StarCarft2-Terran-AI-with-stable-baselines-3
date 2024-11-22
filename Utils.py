import math

import numpy as np
from queue import Queue

import common


class Message:
    def __init__(self, state=None, reward=None, action=None, done=False):
        self.state = state
        self.reward = reward
        self.action = action
        self.done = done


class Memory:
    def __init__(self, action_space_size:int = common.ACTION_SPACE_SIZE, short_term_memory_duration:int=common.MEMORY_SIZE):
        self.memory = np.append(np.zeros(action_space_size), np.full(action_space_size, fill_value=-100))
        self.actions_queue = Queue(maxsize=short_term_memory_duration)
        self.action_space_size = action_space_size


    def register_action(self, action:int, iteration):
        self.memory[action + self.action_space_size] = iteration
        if self.actions_queue.full():
            forgotten_action = self.actions_queue.get_nowait()
            self.memory[forgotten_action] -= 1
        self.actions_queue.put_nowait(action)
        self.memory[action] += 1

    def get_memory(self):
        return self.memory

def create_state(game_map=None, game_info=None):
    if game_map is None:
        game_map = np.zeros(common.OBSERVATION_SPACE_SHAPE_MAP)
    if game_info is None:
        game_info = np.zeros(common.OBSERVATION_SPACE_SHAPE_INFO)
    return {"map": game_map, "info": game_info}

def get_x_y_of_pos(pos, shape):
    return min(math.ceil(pos.x), shape[1] - 1), min(math.ceil(pos.y), shape[0] - 1)
