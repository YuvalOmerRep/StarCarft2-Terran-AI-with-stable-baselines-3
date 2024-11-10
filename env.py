import sys
from typing import Any

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from multiprocessing import Process, Pipe
import Globals as GB
from Utils import Message
from model_bot import run_game_with_model_bot


class Sc2Env(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self, what_to_run="model_bot.py"):
        super(Sc2Env, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(GB.ACTION_SPACE_SIZE)
        self.observation_space = spaces.Box(low=GB.LOW_BOUND, high=GB.HIGH_BOUND,
                                            shape=GB.OBSERVATION_SPACE_SHAPE, dtype=np.float16)
        self.run_sc2 = what_to_run

        self.connection = None

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

        p = Process(target=run_game_with_model_bot, args=(child_conn,))
        p.start()

        state = np.zeros(GB.OBSERVATION_SPACE_SHAPE)
        return state, None
