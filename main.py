import sys

from train_new_model import train_new_model
from load_and_train_model import load_and_train

def main(argv, argc):
    if argv[1] == "new" and argc == 2:
        train_new_model(argv[2])
    elif argv[1] == "train" and argc == 3:
        load_and_train(argv[2], argv[3])
    else:
        raise Exception("improper use")


if __name__ == "__main__":
    main(sys.argv, len(sys.argv))