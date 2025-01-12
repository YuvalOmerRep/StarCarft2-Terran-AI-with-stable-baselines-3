import sys

from sc2.data import Difficulty

from train import train_new_model, load_and_train

COMMAND_TO_DIFFICULTY = {"veryhard": Difficulty.VeryHard,
                         "harder": Difficulty.Harder,
                         "hard": Difficulty.Hard,
                         "mediumhard": Difficulty.MediumHard,
                         "medium": Difficulty.Medium,
                         "easy": Difficulty.Easy}

def get_difficulty_from_string(string: str):
    try:
        difficulty = COMMAND_TO_DIFFICULTY[string]
        return difficulty
    except KeyError:
        raise Exception("Invalid difficulty, options are: easy, medium, hard, harder, veryHard")


def main(argv, argc):
    if argc >= 3 and argv[1] == "new":
        if argc == 3:
            train_new_model(argv[2])
        else:
            train_new_model(argv[2], get_difficulty_from_string(argv[3].lower()))

    elif  argc >= 4 and argv[1] == "train":
        if argc == 4:
            load_and_train(argv[2], argv[3])
        else:
            load_and_train(argv[2], argv[3], get_difficulty_from_string(argv[4].lower()))
    else:
        raise Exception("improper use")


if __name__ == "__main__":
    main(sys.argv, len(sys.argv))