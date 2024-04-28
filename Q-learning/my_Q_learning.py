import random


class World:
    def __init__(self, floor):
        self.world = floor

        self.Q_matrix = self.initialize_Q_matrix()
        self.possible_actions = [0, 1, 2, 3]  # left right up down

    # TODO
    def initialize_Q_matrix(self):
        Q_matrix = self.world
        return Q_matrix

    def check_reward(self, x, y):
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
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.world = world
        self.possible_actions = world.possible_actions

    def adjust_reward(self):
        pass

    def choose_best_action(self):
        pass

    def choose_next_action(self):
        x = random.uniform(0, 1)
        if x > self.epsilon:
            action = self.choose_best_action()
            while self.world.check_collision(action):
                action = self.choose_best_action()
            return action
        else:
            action = random.choice(self.possible_actions)
            while self.world.check_collision(action):
                action = random.choice(self.possible_actions)
            return action

    def move_self(self):
        action = self.choose_next_action()
        movement_vector = calculate_movement_vector(action)
        completed = self.world.move(movement_vector)
        if completed:
            pass
        else:
            self.adjust_reward()


