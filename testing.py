from random import randint, choice


class Shit:
    def __init__(self, tile_num_x, tile_num_y):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y
        self.grid = []

    from random import randint, choice

    def generate_maze(self):
        # Sets up a grid full of walls
        grid = [["#" for _ in range(self.tile_num_x)] for _ in range(self.tile_num_y)]

        # Sets one cell as open, that is not on the edge
        pos = [randint(1, self.tile_num_y - 2), randint(1, self.tile_num_x - 2)]
        grid[pos[0]][pos[1]] = "."

        # List of walls adjacent to open cells, that need to be looked at
        frontier_lst = [[pos[0] + 1, pos[1]], [pos[0] - 1, pos[1]], [pos[0], pos[1] + 1], [pos[0], pos[1] - 1]]

        # Keep track of cells that are open
        open_cells = set()
        open_cells.add(tuple(pos))

        # Checks a wall in frontier list
        while frontier_lst:
            # Chooses a random cell/wall from the frontier list
            cell = choice(frontier_lst)
            y, x = cell

            # Check the four neighbors (up, down, left, right) if any is an open space already
            neighbors = []
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                if (ny, nx) in open_cells:
                    neighbors.append((ny, nx))

            # If exactly one of the neighboring cells is open, then we can consider opening this wall
            if len(neighbors) == 1:
                open_cells.add((y, x))
                grid[y][x] = "."
                # Add new walls to the frontier list, as long as they're actually walls
                # and not out of bounds, and not already in the frontier.
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_y, new_x = y + dy, x + dx
                    if 0 < new_y < self.tile_num_y - 1 and 0 < new_x < self.tile_num_x - 1 and grid[new_y][new_x] == "#":
                        if [new_y, new_x] not in frontier_lst and (new_y, new_x) not in open_cells:
                            frontier_lst.append([new_y, new_x])

            frontier_lst.remove(cell)

        # Adds a solid border to the original grid
        # Border on top and bottom

        for i in range(self.tile_num_x):
            grid[0][i] = '#'
            grid[-1][i] = '#'

        # Border on left and right
        for i in range(1, self.tile_num_y - 1):
            grid[i][0] = '#'
            grid[i][-1] = '#'

        # Store the final grid
        self.grid = grid

    def print_grid(self):
        for line in self.grid:
            print(''.join(line))


if __name__ == '__main__':
    maze = Shit(12, 12)
    maze.generate_maze()
    maze.print_grid()
