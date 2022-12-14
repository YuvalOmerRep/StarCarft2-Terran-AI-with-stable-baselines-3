from stable_baselines3 import PPO
from env import Sc2Env


def play_with_model(model_name: str, from_num_steps, env: Sc2Env, num_of_games):
    """
    A function that loads a model and continues to train it on the sc2 environment

    :param model_name: The model to be loaded
    :param from_num_steps: the number of steps from which to continue training
    :param num_of_games: the number of games the model will play
    :param env: the environment the game will be held on
    """
    LOAD_MODEL = f"models/{model_name}/{from_num_steps}.zip"

    # load the model:
    model = PPO.load(LOAD_MODEL)

    for i in range(num_of_games):
        # Play the game:
        obs = env.reset()
        done = False

        while not done:
            action, _states = model.predict(obs)
            obs, rewards, done, info = env.step(action)


if __name__ == '__main__':
    LOAD_MODEL = f"models/"  # change this to name of model

    # load the model:
    model = PPO.load(LOAD_MODEL)
    env = Sc2Env()

    for i in range(1):  # change this to how many games you want
        # Play the game:
        obs = env.reset()
        done = False

        while not done:
            action, _states = model.predict(obs)
            obs, rewards, done, info = env.step(action)
