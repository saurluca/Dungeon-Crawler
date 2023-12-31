from random import choice
from maze_generator import MazeGenerator


class Maze(MazeGenerator):
    def __init__(self, tile_num_x=9, tile_num_y=9, recursive_weight=4, random_weight=1):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.grid = super().generate_growing_tree_maze(tile_num_x, tile_num_y, recursive_weight, random_weight)

        self.dead_ends = super().search_dead_ends(tile_num_x, tile_num_y, self.grid)
        self.unused_dead_ends = self.dead_ends

        self.free_tiles = []
        self.set_free_tiles()

        self.two_points = self.get_two_distant_points()

        self.generate_stair()

    def __call__(self, x, y):
        return str(self.grid[x][y])

    def set_free_tiles(self):
        for x in range(self.tile_num_y):
            for y in range(self.tile_num_x):
                if self.grid[x][y] == "." and (x, y) not in self.dead_ends:
                    self.free_tiles.append((x, y))

    # TODO for generation of things, not complete random, eg not in hero view range
    # TODO refactor to get_free_tile
    def get_a_free_tile(self):
        free_tile = choice(self.free_tiles)
        self.free_tiles.remove(free_tile)
        return free_tile

    def get_dead_end(self):
        dead_end = choice(self.unused_dead_ends)
        self.unused_dead_ends.remove(dead_end)
        return dead_end

    def set_tile(self, x, y, thing):
        self.grid[x][y] = thing

    def move_object_by(self, x, y, x_direction, y_direction):
        self.grid[x + x_direction][y + y_direction] = self.grid[x][y]
        self.grid[x][y] = "."

    # currently only checking for walls
    def check_obstacle(self, x, y):
        return not self.grid[x][y] == "#"

    # TODO should not be in maze
    def generate_stair(self):
        # x, y = self.get_dead_end()
        # print(x, y)
        x, y = self.two_points[1]
        self.grid[x][y] = "S"

    def print_out(self):
        super().print_out(self.grid)

    # bias hero top left
    # approximation
    def get_two_distant_points(self):
        longest = 0
        two_points = ((0, 0), (0, 0))

        for x1, y1 in self.dead_ends:
            for x2, y2 in self.dead_ends:
                if x1 == x2 and y1 == y2:
                    continue
                distance = abs(x2 - x1) + abs(y2 - y1)
                if distance > longest:
                    longest = distance
                    two_points = ((x1, y1), (x2, y2))

        self.unused_dead_ends.remove(two_points[0])
        self.unused_dead_ends.remove(two_points[1])
        return two_points


if __name__ == '__main__':
    maze = Maze(11, 11)
    maze.print_out()
