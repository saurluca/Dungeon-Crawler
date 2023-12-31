

class Maze:
    def __init__(self):
        self.grid = [["." for i in range(5)] for j in range(5)]

    def print_out(self):
        for row in self.grid:
            for tile in row:
                print(tile, end="")
            print("")

if __name__ == '__main__':
    maze = Maze()
    maze.print_out()
