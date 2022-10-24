from stable_baselines3 import PPO
import os
from env import Sc2Env
import time
import Globals as GB


def train_new_model(model_name: str, env: Sc2Env):
    """
    A function that trains a new model using the sc2 environment

    :param model_name: The name of the new model, model will be saved in models/[model_name]
    :param env: the environment the training will be held on
    """
    model_name = f"{model_name}_{int(time.time())}"

    models_dir = f"models/{model_name}/"
    logdir = f"logs/{model_name}/"

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)

    iters = 0
    while True:
        print("On iteration: ", iters)
        iters += 1
        model.learn(total_timesteps=GB.total_steps, reset_num_timesteps=False, tb_log_name=f"PPO")
        model.save(f"{models_dir}/{GB.total_steps * iters}")
