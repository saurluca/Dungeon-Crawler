import time
from random import choice, randint
from maze_generator import MazeGenerator


class Maze(MazeGenerator):
    def __init__(self, tile_num_x=15, tile_num_y=15, recursive_weight=4, random_weight=1):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.grid = super().generate_growing_tree_maze(tile_num_x, tile_num_y, recursive_weight, random_weight)

        self.dead_ends = super().search_dead_ends(tile_num_x, tile_num_y, self.grid)
        self.unused_dead_ends = self.dead_ends

        self.free_tiles = []
        self.set_free_tiles()

        self.start_hero_pos = self.get_dead_end()

    def __call__(self, x, y):
        return str(self.grid[x][y])

    def set_free_tiles(self):
        for x in range(self.tile_num_y):
            for y in range(self.tile_num_x):
                if self.grid[x][y] == "." and (x, y) not in self.dead_ends:
                    self.free_tiles.append((x, y))

    def set_tile(self, x, y, thing):
        self.grid[x][y] = thing

    # TODO fix, coins and food moved by one tile if stepped on
    def move_entity(self, x, y, new_x, new_y):
        self.grid[new_x][new_y] = self.grid[x][y]
        # checks if the entity is standing on something
        if len(str(self.grid[x][y])) > 1:
            # print(str(self.grid[x][y]))
            self.grid[x][y] = str(self.grid[x][y])[1]
            # print(self.grid[x][y])
        else:
            self.grid[x][y] = "."
        # self.grid[x][y] = str(self.grid[x][y])[1]

    def move_object_by(self, x, y, x_direction, y_direction):
        self.grid[x + x_direction][y + y_direction] = self.grid[x][y]
        self.grid[x][y] = "."

    # old version
    # def check_obstacle2(self, x, y):
    #     return not (self.grid[x][y] == "#" or str(self.grid[x][y]) == "E")

    # tiles that are not walk through
    blockers = set("#HE")
    # TODO what about items for enemies? put them into a corner, and then?

    def check_obstacle(self, x, y):
        return not self.blockers & set(str(self.grid[x][y]))

    def check_see_through(self, x, y):
        return not self.grid[x][y] == "#"

    def print_out(self):
        super().print_out(self.grid)

    def get_free_tile(self):
        free_tile = choice(self.free_tiles)
        self.free_tiles.remove(free_tile)
        return free_tile

    def get_viable_tiles(self, x, y):
        viable_tiles = []
        for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            if self.check_obstacle(x + dx, y + dy):
                viable_tiles.append((x + dx, y + dy))
        return viable_tiles

    def get_dead_end(self):
        dead_end = choice(self.unused_dead_ends)
        self.unused_dead_ends.remove(dead_end)
        return dead_end

    # only an approximation of distance, not actual walk distance
    # TODO fuck you break
    def generate_stair_pos2(self):
        long_len = 3
        distant_points = [(0, (0, 0)) for _ in range(long_len)]
        x1, y1 = self.start_hero_pos

        for x2, y2 in self.unused_dead_ends:
            distance = abs(x2 - x1) + abs(y2 - y1)
            minimum = (min(self.tile_num_x, self.tile_num_y)) // 2
            if distance > minimum and distance > distant_points[-1][0]:
                for i in range(long_len):
                    if distance > distant_points[i][0]:
                        distant_points[i] = (distance, (x2, y2))
                        break

        # ensures distance not 0, because of default assignment
        while True:
            a = choice(distant_points)
            if a[0] != 0:
                return a[1]

    def generate_stair_pos3(self):
        """using the unused_dead_ends list this method returns an object of that list calculating the distances between the
        dead_end and the Hero position increasing the chance of more distant dead_ends being chosen
        """
        dead_ends = self.unused_dead_ends
        # print(dead_ends)
        list_distance = []
        distances = []
        x1, y1 = self.start_hero_pos
        for i in range(0, len(dead_ends)):
            x2, y2 = dead_ends[i]
            distances.append(abs(x2 - x1) + abs(y2))
            list_distance.append(100 * (abs(x2 - x1) + abs(y2 - y1)))
            # print(list_distance)
            if i > 0:
                list_distance[i] += list_distance[i - 1]

        a = randint(0, list_distance[-1])
        # print(list_distance)
        # print(distances)
        # print(f"a: {a} list_distance: {list_distance[-1]}")
        # print(x1, y1)
        for i in range(len(list_distance)):
            if a <= list_distance[i]:
                # return dead_ends[i]
                return dead_ends[i]


def test1():
    average = 0
    n_times = 1000
    for i in range(n_times):
        maze = Maze(15, 15)
        average += maze.generate_stair_pos3()
    print(average / n_times)


def test2():
    total_time1 = 0
    total_time2 = 0
    n_times = 1000
    for i in range(n_times):
        maze = Maze(15, 15)
        start_time = time.time()
        maze.generate_stair_pos2()
        total_time1 += time.time() - start_time
    for i in range(n_times):
        maze = Maze(15, 15)
        start_time = time.time()
        maze.generate_stair_pos3()
        total_time2 += time.time() - start_time

    print(100 * total_time1)
    print(100 * total_time2)


if __name__ == '__main__':
    test2()
