import sys

from train import train_new_model, load_and_train

def main(argv, argc):
    if argc == 3 and argv[1] == "new":
        train_new_model(argv[2])
    elif  argc == 4 and argv[1] == "train":
        load_and_train(argv[2], argv[3])
    else:
        raise Exception("improper use")


if __name__ == "__main__":
    main(sys.argv, len(sys.argv))