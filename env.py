import gym
from gym import spaces
import numpy as np
import subprocess
import pickle
import os
import Globals as GB


class Sc2Env(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self, what_to_run="model_bot.py"):
        super(Sc2Env, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(GB.ACTION_SPACE_SIZE)
        self.observation_space = spaces.Box(low=GB.LOW_BOUND, high=GB.HIGH_BOUND,
                                            shape=GB.OBSERVATION_SPACE_SHAPE, dtype=np.uint8)
        self.run_sc2 = what_to_run

    def step(self, action):
        wait_for_action = True
        # waits for action.
        while wait_for_action:
            try:
                with open('state_rwd_action.pkl', 'rb') as f:
                    state_rwd_action = pickle.load(f)

                    if state_rwd_action['action'] is not None:
                        # Waiting for agent to complete action execution
                        wait_for_action = True
                    else:
                        # Send a new action to agent since agent is done with last one
                        wait_for_action = False
                        state_rwd_action['action'] = action
                        with open('state_rwd_action.pkl', 'wb') as f:
                            # now we've added the action.
                            pickle.dump(state_rwd_action, f)
            except Exception as e:
                # print(str(e))
                pass

        # waits for the new state to return
        wait_for_state = True
        while wait_for_state:
            try:
                if os.path.getsize('state_rwd_action.pkl') > 0:
                    with open('state_rwd_action.pkl', 'rb') as f:
                        state_rwd_action = pickle.load(f)
                        if state_rwd_action['action'] is None:
                            # continue waiting for state
                            wait_for_state = True
                        else:
                            # Got state
                            # action = state_rwd_action['action']
                            state = state_rwd_action['state']
                            reward = state_rwd_action['reward']
                            done = state_rwd_action['done']
                            wait_for_state = False
                            # action = [action]
                            # action.extend(state)
                            # action.append(reward)
                            # self.data_scraper.scrape_data(np.array(action))

            except Exception as e:
                wait_for_state = True
                # todo: state, maybe change this whole section
                state = np.zeros(GB.OBSERVATION_SPACE_SHAPE)
                observation = state
                # if still failing, input an ACTION, 3
                data = {"state": state, "reward": 0, "action": 3,
                        "done": False}  # empty action waiting for the next one!
                with open('state_rwd_action.pkl', 'wb') as f:
                    pickle.dump(data, f)

                state = None
                reward = 0
                done = False
                action = 3

        info = {}
        observation = state
        return observation, reward, done, info

    def reset(self):
        print("RESETTING ENVIRONMENT!!!!!!!!!!!!!")
        state = np.zeros(GB.OBSERVATION_SPACE_SHAPE)
        observation = state
        data = {"state": state, "reward": 0, "action": None, "done": False}  # empty action waiting for the next one!
        with open('state_rwd_action.pkl', 'wb') as f:
            pickle.dump(data, f)

        subprocess.Popen(['python3', self.run_sc2])
        return observation  # reward, done, info can't be included
