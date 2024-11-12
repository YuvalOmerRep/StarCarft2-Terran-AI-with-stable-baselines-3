import numpy as np

import common


class Message:
    def __init__(self, state=None, reward=None, action=None, done=False):
        self.state = state
        self.reward = reward
        self.action = action
        self.done = done


def create_state(game_map=None, game_info=None):
    if game_map is None:
        game_map = np.zeros(common.OBSERVATION_SPACE_SHAPE_MAP)
    if game_info is None:
        game_info = np.zeros(common.OBSERVATION_SPACE_SHAPE_INFO)
    return {"map": game_map, "info": game_info}
