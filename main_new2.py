import arcade


class Game(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()

    def update(self, delta_time):
        pass


def main():
    window = Game(600, 600, "My Game")
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
