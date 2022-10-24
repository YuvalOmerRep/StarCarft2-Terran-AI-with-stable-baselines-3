from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game, run_multiple_games, GameMatch
from sc2.data import Race, Difficulty
from Random_Terran_Bot import RandomTerranBot
from sc2.data import Result
import Globals as GB


def run_single_game():
    my_bot = Bot(Race.Terran, RandomTerranBot())
    computer = Computer(Race.Protoss, Difficulty.VeryEasy)
    print(run_game(maps.get("JagannathaAIE"), [my_bot, computer],
                   realtime=False, disable_fog=True))


def run_num_of_games_against_same_computer(num: int, difficulty, my_bot):
    computer = Computer(Race.Protoss, difficulty)
    match = GameMatch(map_sc2=maps.get("JagannathaAIE"), players=[my_bot, computer],
                      disable_fog=True, game_time_limit=GB.GAME_TIME_LIMIT)

    results = run_multiple_games([match for i in range(num)])

    results_my_bot = {Result.Victory: 0, Result.Defeat: 0, Result.Tie: 0}

    for result in results:
        results_my_bot[result[my_bot]] += 1

    print(f"Random Bot has won {results_my_bot[Result.Victory]}, lost {results_my_bot[Result.Defeat]} and tied "
          f"{results_my_bot[Result.Tie]} in {num} games against a computer with {difficulty} difficulty")
