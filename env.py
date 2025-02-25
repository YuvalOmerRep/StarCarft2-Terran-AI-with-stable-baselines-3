import sys
from typing import Any

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from multiprocessing import Process, Pipe

from sc2.data import Difficulty

import common
import Utils
from Utils import Message
from model_bot import run_game_with_model_bot


class Sc2Env(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self, difficulty=Difficulty.Hard):
        super(Sc2Env, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.MultiDiscrete(common.ACTION_SPACE_SIZE)
        self.observation_space = spaces.Dict({"map": spaces.Box(low=0, high=255, shape=common.OBSERVATION_SPACE_SHAPE_MAP, dtype=np.uint8),
                                              "info": spaces.Box(low=common.LOW_BOUND, high=common.HIGH_BOUND, shape=common.OBSERVATION_SPACE_SHAPE_INFO, dtype=np.float16)})
        self.connection = None
        self.difficulty = difficulty

    def _recv_type(self, message_type: type):
        message = self.connection.recv()
        if type(message) != message_type:
            print(f"message was expected to be of type {message_type}", file=sys.stderr)
            raise TypeError
        return message

    def step(self, action):
        action_message = Message(action=action)
        self.connection.send(action_message)

        state_message = self.connection.recv()
        return state_message.state, state_message.reward, state_message.done, {}, {}

    def reset(self,
              *,
              seed: int | None = None,
              options: dict[str, Any] | None = None):
        print("RESETTING ENVIRONMENT!!!!!!!!!!!!!")
        if self.connection is not None:
            self.connection.close()
        father_conn, child_conn = Pipe()
        self.connection = father_conn

        p = Process(target=run_game_with_model_bot, args=(child_conn,self.difficulty))
        p.start()

        state = Utils.create_state()
        return state, None
