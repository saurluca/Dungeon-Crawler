import random
class World:
    """Represents the board. It's separated from the state because the board is static."""

    def __init__(self, maze):
        """Initialise the board."""
        self.rows = maze.tile_num_y
        self.cols = maze.tile_num_x
        self.win = maze.stair_pos
        self.maze = maze

    def is_end(self, state):
        """Return True if the state is a terminal state, False otherwise."""
        return state == self.win

    def reward(self, state):
        if self.maze(*state) == "c":
            return 1
        elif self.maze(*state) == "#":
            return -0.5
        elif self.maze(*state) == "D":
            return 10
        else:
            return -0.1

    def next(self, state, action):
        """Return the next state given the current state and action.

        Actions:
        w: up
        s: down
        a: left
        d: right

        State is a tuple (x, y) where x is the row and y is the column."""
        x_pos = state[0]
        y_pos = state[1]
        if action == "w" and not self.maze.is_wall(x_pos - 1, y_pos):
            return x_pos - 1, y_pos  # up
        elif action == "s" and not self.maze.is_wall(x_pos + 1, y_pos):
            return x_pos + 1, y_pos  # down
        elif action == "a" and not self.maze.is_wall(x_pos, y_pos - 1):
            return x_pos, y_pos - 1  # left
        elif action == "d" and not self.maze.is_wall(x_pos, y_pos + 1):
            return x_pos, y_pos + 1  # right
        else:
            return state
class State:
    """Represents a current state, can print the board with current position."""

    def __init__(self, hero, world):
        """Initialise the state."""
        self.state = hero.pos
        self.world = world
        self.is_end = self.world.is_end(self.state)

    def reward(self):
        """Return the reward for the current state."""
        return self.world.reward(self.state)

    def next(self, action):
        """Return the next state given the current state and action."""
        return self.world.next(self.state, action)


class Agent:
    """Implements a Q-learning agent in a grid world."""

    def __init__(self, maze, hero, alpha=0.5, gamma=0.9, epsilon=0.1):
        """Initialize states and actions.

        :param alpha = learning rate (between 0 and 1)
        :param gamma = discount factor (future rewards)
        :param epsilon = probability of not following best action (epsilon-greedy strategy)
        """

        self.states = []
        self.actions = ["w", "s", "a", "d"]  # up, down, left, right
        self.world = World(maze)
        self.state = State(hero, self.world)

        # set the learning and greedy values
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # value for epsilon-greedy policy

        self.is_end = self.state.is_end

        # array to retain reward values for plot
        self.plot_reward = []

        self.rewards = 0  # accumulated rewards

        # initalise all Q values across the board to 0
        self.Q = {}
        for i in range(self.world.rows):
            for j in range(self.world.cols):
                for k in range(len(self.actions)):
                    self.Q[(i, j, k)] = 0


    def Action(self):
        """Choose an action based on epsilon-greedy policy, and move to the next state.

        :returns (position: tuple of the next state, action: the action chosen)."""

        # random value vs epsilon
        rnd = random.random()
        # set arbitrary low value to compare with Q values to find max
        max_next_reward = -10
        action = None

        # 9/10 find max Q value over actions
        if rnd > self.epsilon:
            # iterate through actions, find Q  value and choose best
            for k in self.actions:
                print(self.state)
                i, j = self.state
                next_reward = self.Q[(i, j, k)]
                if next_reward >= max_next_reward:
                    action = k
                    max_next_reward = next_reward
        # else choose random action
        else:
            action = random.choice(self.actions)

        # select the next state based on action chosen
        position = self.state.next(action)
        return position, action

    def Q_Learning(self, episodes):
        """Q-Learning algorithm to find the best path through the grid.

        :param episodes: number of episodes to run the algorithm for.
        :returns nothing"""

        x = 0
        # each episode: Move until an end state is reached
        while (x < episodes):

            if self.is_end:  # end state?

                reward = self.state.reward()
                self.rewards += reward
                self.plot_reward.append(self.rewards)  # add accumulated rewards to plot

                # get state, assign reward to each Q_value in state
                i, j = self.state.state
                for a in self.actions:
                    # self.new_Q[(i,j,a)] = round(reward,3)
                    self.Q[(i, j, a)] = round(reward, 3)

                # reset state
                self.state = State(world=self.state.world)
                self.is_end = self.state.is_end

                # set rewards to zero and iterate to next episode
                self.rewards = 0
                x += 1
            else:
                # set to arbitrary low value to compare net state actions
                max_next_value = -10

                # get current state, next state, action and current reward
                next_state, action = self.Action()
                i, j = self.state.state
                reward = self.state.reward()

                self.rewards += reward  # add reward to rewards for plot

                # iterate through actions to find max Q value for action based on next state action
                for a in self.actions:
                    nextStateAction = (next_state[0], next_state[1], a)
                    q_value = (1 - self.alpha) * self.Q[(i, j, action)] + self.alpha * (
                                reward + self.gamma * self.Q[nextStateAction])

                    # find largest Q value
                    if q_value >= max_next_value:
                        max_next_value = q_value

                # next state is now current state, check if end state
                self.state = State(state=next_state, world=self.state.world)
                self.is_end = self.state.is_end

                # update Q values with max Q value for next state
                self.Q[(i, j, action)] = round(max_next_value, 3)

            # copy new Q values to Q table
            # self.Q = self.new_Q.copy()
