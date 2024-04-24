import random
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
        self.world = maze
        self.state = hero.pos

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
        for i in range(self.world.tile_num_y):
            for j in range(self.world.tile_num_x):
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
                i, j = self.state.state
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
        while x < episodes:

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
                self.state = self.state.pos
             #   self.is_end = self.state.is_end

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

