import sys

from sc2.data import Difficulty

from train import train_new_model, load_and_train

COMMAND_TO_DIFFICULTY = {"veryHard": Difficulty.VeryHard,
                         "harder": Difficulty.Harder,
                         "hard": Difficulty.Hard,
                         "mediumHard": Difficulty.MediumHard,
                         "medium": Difficulty.Medium,
                         "easy": Difficulty.Easy}

def get_difficulties_from_string(string: str) -> list[Difficulty]:
    try:
        res = []
        for difficulty in string.split(","):
            res.append(COMMAND_TO_DIFFICULTY[difficulty])
        return res
    except KeyError:
        raise Exception("Invalid difficulty detected, options are: easy, medium, hard, harder, veryHard")


def main(argv, argc):
    if argc >= 3 and argv[1] == "new":
        if argc == 3:
            train_new_model(argv[2], [Difficulty.Hard])
        else:
            train_new_model(argv[2], get_difficulties_from_string(argc[3]))

    elif  argc >= 4 and argv[1] == "train":
        if argc == 4:
            load_and_train(argv[2], argv[3], [Difficulty.Hard])
        else:
            load_and_train(argv[2], argv[3], get_difficulties_from_string(argv[4]))
    else:
        raise Exception("improper use")


if __name__ == "__main__":
    main(sys.argv, len(sys.argv))