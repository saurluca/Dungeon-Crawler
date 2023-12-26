
class Hero:
    def __init__(self, maze):
        self.maze = maze

        # spawn in random position
        self.x, self.y = self.maze.get_a_free_tile()
        self.maze.set_tile(self.x, self.y, self)

    def __call__(self):
        return "H"

    def get_position(self):
        return self.x, self.y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
