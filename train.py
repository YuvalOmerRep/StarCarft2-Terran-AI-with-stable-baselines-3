from stable_baselines3 import PPO
import os
from env import Sc2Env
import time
import common
import torch


def train_new_model(model_name: str):
    """
    A function that trains a new model using the sc2 environment

    :param model_name: The name of the new model, model will be saved in models/[model_name]
    :param env: the environment the training will be held on
    """
    model_name = f"{model_name}_{int(time.time())}"
    env = Sc2Env()
    models_dir = f"models/{model_name}/"
    logdir = f"logs/{model_name}/"

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir, device=torch.device('cuda'))

    iters = 0
    while True:
        print("On iteration: ", iters)
        iters += 1
        model.learn(total_timesteps=common.total_steps, reset_num_timesteps=False, tb_log_name=f"PPO")
        model.save(f"{models_dir}/{common.total_steps * iters}")


def load_and_train(model_name: str, from_num_steps: str):
    """
    A function that loads a model and continues to train it on the sc2 environment

    :param model_name: The model to be loaded
    :param from_num_steps: the number of steps from which to continue training
    """
    load_model = f"models/{model_name}/{from_num_steps}.zip"

    # load the model:
    model = PPO.load(load_model, env=Sc2Env())

    models_dir = f"models/{model_name}/"

    # further train:
    was_at_iter = int(from_num_steps)
    iters = 0
    while True:
        print("On iteration: ", iters)
        iters += 1
        model.learn(total_timesteps=common.total_steps, reset_num_timesteps=False, tb_log_name=f"PPO")
        model.save(f"{models_dir}/{common.total_steps * iters + was_at_iter}")

if __name__ == '__main__':
    train_new_model(model_name=f"model_v2")
