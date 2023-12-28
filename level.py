from maze import Maze
from hero import Hero


class Level:
    def __init__(self, tile_num_x, tile_num_y):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.maze = None
        self.hero = None

        self.coin_list = None
        self.coin_count = None

    def set_up(self):
        self.maze = Maze(self.tile_num_x, self.tile_num_y)
        self.hero = Hero(*self.maze.get_a_free_tile())
