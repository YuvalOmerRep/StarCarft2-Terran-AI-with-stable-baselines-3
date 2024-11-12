import torch
from tensordict.nn.distributions import NormalParamExtractor
from torch import nn
import torch.nn.functional as F
import common

num_cells = 256  # number of cells in each layer i.e. output dim.


class Actor(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 5, 3)
        self.conv2 = nn.Conv2d(5, 10, 3)
        self.conv3 = nn.Conv2d(10, 4, 3)
        self.fc_image = nn.LazyLinear(100)
        self.fc1 = nn.LazyLinear(num_cells)
        self.fc2 = nn.LazyLinear(num_cells)
        self.fc3 = nn.LazyLinear(2 * common.OBSERVATION_SPACE_SHAPE_MAP.shape[-1])
        self.pool = nn.MaxPool2d(2)
        self.param_ex = NormalParamExtractor()

    def forward(self, inp):  # todo: will definitely have some dimension problems
        observation, game_map = inp[:, :87], inp[:, 88]
        game_map = F.relu(self.conv1(game_map))
        game_map = self.pool(game_map)
        game_map = F.relu(self.conv2(game_map))
        game_map = self.pool(game_map)
        game_map = F.relu(self.conv3(game_map))
        game_map = self.pool(game_map)
        game_map = torch.flatten(game_map, 1)  # flatten all dims except batch dim
        game_map = F.relu(self.fc_image(game_map))
        X = torch.cat((observation, game_map), 1)
        X = F.tanh(self.fc1(X))
        X = F.tanh(self.fc2(X))
        X = F.tanh(self.fc3(X))
        return self.param_ex(X)
