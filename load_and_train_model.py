import sys

from stable_baselines3 import PPO
from env import Sc2Env
import time
import Globals as GB


def load_and_train(model_name: str, from_num_steps: str):
    """
    A function that loads a model and continues to train it on the sc2 environment

    :param model_name: The model to be loaded
    :param from_num_steps: the number of steps from which to continue training
    :param new_model_name: the name under the new model will be saved
    :param env: the environment the training will be held on
    """
    LOAD_MODEL = f"models/{model_name}/{from_num_steps}.zip"

    # load the model:
    model = PPO.load(LOAD_MODEL, env=Sc2Env())

    models_dir = f"models/{model_name}/"

    # further train:
    was_at_iter = int(from_num_steps)
    iters = 0
    while True:
        print("On iteration: ", iters)
        iters += 1
        model.learn(total_timesteps=GB.total_steps, reset_num_timesteps=False, tb_log_name=f"PPO")
        model.save(f"{models_dir}/{GB.total_steps * iters + was_at_iter}")

