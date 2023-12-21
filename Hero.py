from algoviz.svg import SVGView, Circle
from random import choice


class Hero:
    def __init__(self, maze):
        self.maze = maze
        self.view = maze.view
        self.tile_size = maze.tile_size

        self.y = 0
        self.x = choice([i for i in range(maze.tile_num_x) if self.maze[0][i] == "."])
        maze.set_tile(self.x, self.y, self)

        # drawing
        self.radius = 6
        self.offset = self.tile_size / 2
        self.drawing = Circle(self.x * self.tile_size + self.offset, self.y * self.tile_size + self.offset, self.radius, self.view)
        self.drawing.set_fill_rgb(20, 150, 20)

    def move_by(self, x_direction, y_direction):
        self.maze.move_object_by(self.x, self.y, x_direction, y_direction)
        self.drawing.move_by(x_direction * self.tile_size, y_direction * self.tile_size)
        self.x += x_direction
        self.y += y_direction

