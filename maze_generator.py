from random import choice, randint


def check_unvisited_neighbors(current_cell, visited, tile_num_x, tile_num_y):
    open_neighbors = []
    for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        neighbor_cell = (current_cell[0] + dx, current_cell[1] + dy)
        if 0 < neighbor_cell[0] < tile_num_x - 1 and 0 < neighbor_cell[1] < tile_num_y - 1 and neighbor_cell not in visited:
            open_neighbors.append(neighbor_cell)
    return open_neighbors


def in_between(x1, y1, x2, y2):
    if x1 < x2:
        return x2 - 1, y1
    elif x1 > x2:
        return x2 + 1, y1
    elif y1 < y2:
        return x2, y2 - 1
    elif y1 > y2:
        return x2, y2 + 1


def generate_alternating_grid(tile_num_x, tile_num_y):
    grid = [["#" for _ in range(tile_num_y)]]
    for x in range(tile_num_x-3):
        flip = True
        row = []
        for y in range(tile_num_y):
            row.append("#") if flip else row.append(".")
            flip = not flip
        grid.append(row)
        grid.append(["#" for _ in range(tile_num_y)])
    return grid


class MazeGenerator:

    # generates a grid using prims algorithm
    # "#" represents a wall, "." a free tile
    @staticmethod
    def generate_prim_maze(tile_num_x, tile_num_y):
        # sets up a grid full of walls
        grid = [["#" for _ in range(tile_num_x - 2)] for _ in range(tile_num_y - 2)]

        def check(y, x, value):
            if 0 <= y < tile_num_y - 3 and 0 <= x < tile_num_x - 3:
                if grid[y][x] == value:
                    return True
            return False

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

    def print_out(self, grid):
        for row in grid:
            for tile in row:
                print(tile, end="")
            print("")

    # only uneven x and y num, otherwise ugly
    @staticmethod
    def generate_growing_tree_maze(tile_num_x, tile_num_y):
        grid = generate_alternating_grid(tile_num_x, tile_num_y)

        # TODO implement start at a random position
        visited = [(1, 1)]

        # -2 because of wall border, // 2 + 1 to half it and round up, of x and y tiles
        num_free_tiles = ((tile_num_x - 2) // 2 + 1) * ((tile_num_y - 2) // 2 + 1)
        i = 0
        not_found = 0
        while i < num_free_tiles - 1:
            # here change selection method of next cell
            # this is similar to a recursive backtracking algorithm
            current_cell = visited[-1 - not_found]

            # this is similar to Prim's algorithm
            # current_cell = choice(visited)

            open_neighbors = check_unvisited_neighbors(current_cell, visited, tile_num_x, tile_num_y)

            if open_neighbors:
                next_cell = choice(open_neighbors)
                x, y = in_between(*current_cell, *next_cell)
                grid[x][y] = "."
                visited.append(next_cell)
                i += 1
                not_found = 0
            else:
                not_found += 1

        return grid


if __name__ == '__main__':
    mg = MazeGenerator()
    # mg.print_out(generate_alternating_grid(5, 5))
    grid = mg.generate_growing_tree_maze(7, 7)
    mg.print_out(grid)
