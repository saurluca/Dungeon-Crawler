import random as r


# constant Q values
EMPTY_TILE_VALUE = -0.05
WALL_VALUE = -1
STAIR_VALUE = 10


class World:
    def __init__(self, floor, initialization_method):
        self.world = floor
        self.initialization_method = initialization_method

        self.Q_matrix = self.initialize_Q_matrix()
        self.possible_actions = [0, 1, 2, 3]  # left right up down

    def initialize_Q_matrix(self):
        maze = self.world.maze
        maze_size_x, maze_size_y = maze.get_tile_num_x, maze.get_tile_num_y

        # TODO do I need a 3D array to have a Q value for each state action pair?
        # initialize Q_matrix with random reward values between 0 and 1
        Q_matrix = [[self.assign_start_Q_value() for _ in range(maze_size_x)] for _ in range(maze_size_y)]
        for x in range(len(maze_size_x)):
            for y in range(len(maze_size_y)):
                tile = maze[x][y]
                if tile == "#":
                    Q_matrix[x][y] = WALL_VALUE
                elif tile == "D":
                    Q_matrix[x][y] = STAIR_VALUE
        return Q_matrix

    def assign_start_Q_value(self):
        if self.initialization_method == "random_positive":
            return r.uniform(0, 1)
        if self.initialization_method == "random_negative":
            return r.uniform(-1, 0)
        if self.initialization_method == "random_all":
            return r.uniform(-1, 1)
        if self.initialization_method == "flat_negative":
            return EMPTY_TILE_VALUE
        if self.initialization_method == "zero":
            return 0
        raise Exception("Invalid initialization method")

    def get_reward(self, x, y):
        return self.Q_matrix[x][y]

    def check_collision(self, x, y):
        return self.world.check_obstacle(x, y)

    def move(self, movement_vector):
        self.world.move_hero(movement_vector)
        return self.world.check_completed()


def calculate_movement_vector(next_action):
    return [(-1, 0), (1, 0), (0, 1), (0, -1)][next_action]


class Agent:
    def __init__(self, alpha, gamma, epsilon, world):
        """Initialize states and actions.

        :param alpha = learning rate (between 0 and 1)
        :param gamma = discount factor (future rewards)
        :param epsilon = probability of not following best action (epsilon-greedy strategy)
        """
        # set the learning and greedy values
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # value for epsilon-greedy policy
        self.world = world
        self.possible_actions = world.possible_actions

    def adjust_reward(self, x, y, new_x, new_y):
        reward = self.calculate_new_reward(x, y, new_x, new_y)

    def calculate_new_reward(self, x, y, new_x, new_y):
        current_reward = self.world.get_reward(x, y)
        # TODO complete this equation
        new_reward = current_reward + self.alpha * (self.world.get_reward(new_x, new_y) + self.gamma - current_reward)

        return new_reward

    def choose_best_action(self):
        # TODO
        pass

    def choose_next_action(self):
        x = r.uniform(0, 1)
        if x > self.epsilon:
            action = self.choose_best_action()
            # Does not allow agent to choose action to walk into wall, instead chooses again
            while self.world.check_collision(action):
                action = self.choose_best_action()
            return action
        else:
            action = r.choice(self.possible_actions)
            # Does not allow agent to choose action to walk into wall, instead chooses again
            while self.world.check_collision(action):
                action = r.choice(self.possible_actions)
            return action

    def move_self(self):
        action = self.choose_next_action()
        movement_vector = calculate_movement_vector(action)
        completed = self.world.move(movement_vector)
        if completed:
            pass
        else:
            self.adjust_reward()
