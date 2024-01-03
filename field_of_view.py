"""
the purpose of this class it to check the field of view of the hero
then returns the tiles that are uncovered for the first time
"""

VIEW_RANGE = 3


class FieldOfView:
    def __init__(self, maze):
        self.maze = maze
        self.view_range = VIEW_RANGE
        self.tile_num_x, self.tile_num_y = maze.get_tile_num()

        self.view_range_mask = self.create_view_range_mask()
        self.uncovered_tiles = [[False for _ in range(self.tile_num_y)] for _ in range(self.tile_num_x)]
        self.new_tiles = None

    def create_view_range_mask(self):
        mask = []
        # center of field of view
        rx, ry = self.view_range, self.view_range
        for x in range(self.view_range * 2 + 1):
            row = []
            for y in range(self.view_range * 2 + 1):
                # if the relative x and y are not within the wanted field of view, set True
                row.append((abs(rx - x) + abs(ry - y) <= self.view_range))
            mask.append(row)
        return mask

    # TODO: make more efficient
    def calculate_fov(self, cx, cy):
        # hero position in the relative grid
        rx, ry = self.view_range, self.view_range

        new_tiles = []
        for x in range(self.view_range * 2 + 1):
            for y in range(self.view_range * 2 + 1):
                # center of hero x + (vector of center hero to view range grid)
                abs_x = cx + (x - rx)
                abs_y = cy + (y - ry)
                # checks if in circular view range, if in bound of grid, that the block is in line of sight, block not seen before
                if self.view_range_mask[x][y] and self.in_bound(abs_x, abs_y) and self.check_block_visible(cx, cy, rx, ry, x, y) and not \
                        self.uncovered_tiles[abs_x][abs_y]:
                    new_tiles.append((abs_x, abs_y))
                    self.uncovered_tiles[abs_x][abs_y] = True

        return new_tiles

    # calculates line approximation and checks if sight is blocked along the line
    def check_block_visible(self, cx, cy, rx, ry, x, y):
        s = get_line((rx, ry), (x, y))
        for point in s:
            if not self.maze.check_obstacle(cx + point[0] - rx, cy + point[1] - ry) and point != (x, y):
                return False
        return True

    def in_bound(self, x, y):
        return 0 <= x < self.tile_num_x and 0 <= y < self.tile_num_y


def get_line(start, end):
    """
    This method returns a list of points that approximate a line between a start and end point
    """
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1

    is_steep = abs(dy) > abs(dx)

    # rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points
