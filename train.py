from sc2.data import Difficulty
from stable_baselines3 import PPO
import os
from env import Sc2Env
import time
import common
import torch


def _train(model: PPO, models_dir: str, was_at_iteration: int):
    iters = 0
    while True:
        iters += 1
        print("On iteration: ", iters)
        model.learn(total_timesteps=common.total_steps, reset_num_timesteps=False, tb_log_name=f"PPO")
        model.save(f"{models_dir}/{iters + was_at_iteration}")


def train_new_model(model_name: str, difficulty=Difficulty.Hard):
    """
    A function that trains a new model using the sc2 environment

    :param model_name: The name of the new model, model will be saved in models/[model_name]
    :param difficulty: the difficulty of the bot the model trains against
    """
    env = Sc2Env(difficulty=difficulty)
    models_dir = f"models/{model_name}/"
    logdir = f"logs/{model_name}/"

    if os.path.exists(models_dir):
        raise Exception(f"model with name {model_name} already exists, use with train option if you want to continue training")

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    model = PPO('MultiInputPolicy', env, verbose=1, tensorboard_log=logdir, device=torch.device('cuda'))

    _train(model, models_dir, was_at_iteration=0)

def load_and_train(model_name: str, from_num_steps: str, difficulty=Difficulty.Hard):
    """
    A function that loads a model and continues to train it on the sc2 environment

    :param model_name: The model to be loaded
    :param from_num_steps: the number of steps from which to continue training
    :param difficulty: the difficulty of the bot the model trains against
    """
    load_model = f"models/{model_name}/{from_num_steps}.zip"

    # load the model:
    model = PPO.load(load_model, env=Sc2Env(difficulty=difficulty))

    models_dir = f"models/{model_name}/"

    # further train:
    _train(model, models_dir, was_at_iteration=int(from_num_steps))

if __name__ == '__main__':
    train_new_model(model_name=f"model_v2")
