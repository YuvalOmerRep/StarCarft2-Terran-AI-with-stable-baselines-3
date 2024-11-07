class Message:
    def __init__(self, state=None, reward=None, action=None, done=False):
        self.state = state
        self.reward = reward
        self.action = action
        self.done = done
