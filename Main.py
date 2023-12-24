import arcade
from random import choice
from Maze import Maze
from Hero import Hero

tile_num_x = 16
tile_num_y = 16

character_scaling = 1.8
tile_scaling = 2
tile_size = 32

screen_title = "Dungeon Crawler"
screen_width = tile_num_x * tile_size
screen_height = tile_num_y * tile_size

# either move smooth, half tile or full tile, change update time as well
player_movement_speed = tile_size / 2


class Game(arcade.Window):
    def __init__(self):
        super().__init__(screen_width, screen_height, screen_title)

        self.maze = None
        self.hero = None

        self.scene = None

        self.player_sprite = None

        self.physics_engine = None

        arcade.set_background_color(arcade.csscolor.DARK_GRAY)

    def setup(self):
        self.maze = Maze(tile_num_x, tile_num_y)
        self.hero = Hero(self.maze)

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")

        # renders the walls and the floor
        for y in range(tile_num_y):
            for x in range(tile_num_x):
                if self.maze(x, y) == "#":
                    # random walls and floor tiles to make it look nicer
                    wall_textures = ["Tiles/tile_0014.png", "Tiles/tile_0040.png"]
                    wall = arcade.Sprite(choice(wall_textures), tile_scaling)
                    wall.center_x = x * tile_size + tile_size / 2
                    wall.center_y = y * tile_size + tile_size / 2
                    self.scene.add_sprite("Walls", wall)

                else:
                    floor_textures = ["Tiles/tile_0042.png", "Tiles/tile_0048.png", "Tiles/tile_0049.png"]
                    floor = arcade.Sprite(choice(floor_textures), tile_scaling)
                    floor.center_x = x * tile_size + tile_size / 2
                    floor.center_y = y * tile_size + tile_size / 2
                    self.scene.add_sprite("Floor", floor)

        # renders the hero
        self.player_sprite = arcade.Sprite("Tiles/tile_0098.png", character_scaling)
        self.player_sprite.center_x = self.hero.get_x() * tile_size + tile_size / 2
        self.player_sprite.center_y = self.hero.get_y() * tile_size + tile_size / 2
        self.scene.add_sprite("Player", self.player_sprite)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.scene.get_sprite_list("Walls"))

    def on_draw(self):
        arcade.start_render()

        self.scene.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = player_movement_speed
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = - player_movement_speed
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = player_movement_speed
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = - player_movement_speed

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0

    def update_physics_engine(self, delta_time):
        self.physics_engine.update()

    def on_update(self, delta_time):
        pass


def main():
    window = Game()
    window.setup()

    arcade.schedule(window.update_physics_engine, 1 / 10)

    arcade.run()


if __name__ == "__main__":
    main()
