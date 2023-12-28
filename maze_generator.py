from random import choice, randint


class MazeGenerator:

    # generates a grid using prims algorithm
    # "#" represents a wall, "." a free tile
    @staticmethod
    def generate_prim_maze(tile_num_x, tile_num_y):
        # sets up a grid full of walls
        grid = [["#" for _ in range(tile_num_x - 2)] for _ in range(tile_num_y - 2)]

        # sets one cell as open, that is not on the edge
        (start_y, start_x) = (randint(1, tile_num_y - 4), randint(1, tile_num_x - 4))
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
                if 0 <= y < tile_num_y - 3 and 0 <= x < tile_num_x - 3:
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

        # TODO improve step of adding the border
        # Create the new grid with borders
        border_grid = ['#' * tile_num_x]  # Adds the top border

        # Add left and right borders to the original grid rows
        for row in grid:
            border_grid.append('#' + ''.join(row) + '#')

        border_grid += ['#' * tile_num_x]  # Adds the bottom border

        # converts it back to a list of separate strings
        return [list(row) for row in border_grid]