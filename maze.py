from random import choice
from maze_generator import MazeGenerator


class Maze(MazeGenerator):
    def __init__(self, tile_num_x=12, tile_num_y=12):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.grid = super().generate_prim_maze(tile_num_x, tile_num_y)

        self.free_tiles = []
        self.set_free_tiles()

        self.generate_stair()

    def __call__(self, x, y):
        return str(self.grid[y][x])

    def set_free_tiles(self):
        for y in range(self.tile_num_y):
            for x in range(self.tile_num_x):
                if self.grid[y][x] == ".":
                    self.free_tiles.append((x, y))

    # TODO for generation of things, not complete random, eg not in hero view range
    def get_a_free_tile(self):
        free_tile = choice(self.free_tiles)
        self.free_tiles.remove(free_tile)
        return free_tile

    def set_tile(self, x, y, thing):
        self.grid[y][x] = thing

    def move_object_by(self, x, y, x_direction, y_direction):
        self.grid[y + y_direction][x + x_direction] = self.grid[y][x]
        self.grid[y][x] = "."

    # outputs the grid in the console as a string
    def print_out(self):
        for lines in self.grid:
            for tile in lines:
                print(tile, end="")
            print("")

    # currently only checking for walls
    def check_obstacle(self, x, y):
        return not self.grid[y][x] == "#"

    # TODO should not be in maze
    def generate_stair(self):
        x, y = self.get_a_free_tile()
        self.grid[y][x] = "S"
