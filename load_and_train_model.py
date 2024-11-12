from stable_baselines3 import PPO
from env import Sc2Env
import common


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

