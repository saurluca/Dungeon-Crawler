from random import randint, choice


class Maze:
    def __init__(self, tile_num_x=12, tile_num_y=12):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.grid = []
        self.generate_maze()

        self.free_tiles = []
        self.set_free_tiles()

        self.generate_stair()

    def __call__(self, x, y):
        return str(self.grid[y][x])

    # TODO improv maze gen, no diagonal walls
    # generates a grid using prims algorithm
    # "#" represents a wall, "." a free tile
    def generate_maze(self):
        # sets up a grid full of walls
        grid = [["#" for _ in range(self.tile_num_x - 2)] for _ in range(self.tile_num_y - 2)]

        # sets one cell as open, that is not on the edge
        (start_y, start_x) = (randint(1, self.tile_num_y - 4), randint(1, self.tile_num_x - 4))
        grid[start_y][start_x] = "."

        # list of walls adjacent to an open cells, that need to be looked at
        frontier_lst = [(start_y + 1, start_x), (start_y - 1, start_x), (start_y, start_x + 1), (start_y, start_x - 1)]

        # checks a wall in frontier list
        while frontier_lst:
            # chooses a random cell/wall from the frontier list
            y, x = choice(frontier_lst)
            neighbors = 0
            diagonals = 0

            def check(y, x, value):
                if 0 <= y < self.tile_num_y - 3 and 0 <= x < self.tile_num_x - 3:
                    if grid[y][x] == value:
                        return True
                return False

            # checks for number of neighboring open cells
            for (dy, dx) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_y, new_x = y + dy, x + dx
                if check(new_y, new_x, "."):
                    neighbors += 1

            # check diagonals
            for (dy, dx) in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                new_y, new_x = y + dy, x + dx
                if check(new_y, new_x, "."):
                    connected = False
                    for (cy, cx) in [(new_y, x), (y, new_x)]:
                        if check(cy, cx, "."):
                            connected = True
                    if not connected:
                        diagonals += 1

            # if that wall has exactly one neighbour, make it an open cell
            # and at it's neighboring walls to the frontier list
            if neighbors == 1 and diagonals == 0:
                grid[y][x] = "."
                for (dy, dx) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_y, new_x = y + dy, x + dx
                    if check(new_y, new_x, "#"):
                        frontier_lst.append((new_y, new_x))

            frontier_lst.remove((y, x))

        # improve step of adding the border !!

        # Create the new grid with borders
        border_grid = ['#' * self.tile_num_x]  # Adds the top border

        # Add left and right borders to the original grid rows
        for row in grid:
            border_grid.append('#' + ''.join(row) + '#')

        border_grid += ['#' * self.tile_num_x]  # Adds the bottom border

        # converts it back to a list of separate strings
        self.grid = [list(row) for row in border_grid]

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
