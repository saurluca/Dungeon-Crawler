import arcade
from random import choice
from hero import Hero
from level import Level
import time

# Only odd numbers
TILE_NUM_X = 15
TILE_NUM_Y = 15

# TODO because of this character slightly smaller then tiles
CHARACTER_SCALING = 1.8
TILE_SCALING = 2.0
COIN_SCALING = 1.4
TILE_SIZE = 32

# height should be width +1, to accommodate the ui
SCREEN_TITLE = "Dungeon Crawler"
SCREEN_WIDTH = 15 * TILE_SIZE
SCREEN_HEIGHT = 16 * TILE_SIZE

# cheat mode for full vision
I_SEE_EVERYTHING = False
DIAGONAL_MOVEMENT = True

# either move smooth, half tile or full tile, change update time as well
PLAYER_MOVEMENT_SPEED = TILE_SIZE
VIEW_RANGE = 3

NUM_COINS = 20


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.hero = None
        self.level = None

        # used for interaction between level and main class
        self.player_change_x = 0
        self.player_change_y = 0
        self.coins_collected = 0

        # scene is an object containing all sprites that are currently rendered
        self.scene = None

        # player and coin sprite seperated, so they can be changed dynamically
        self.player_sprite = None
        self.coin_sprites = None

        # player camera
        self.camera = None
        # camera used for gui elements
        self.ui_camera = None

        # keeps track of time spent in a level
        self.start_time = None
        self.time_text = None

        # keeps track of and displays the score, currently coins collected
        self.score = 0
        self.score_text = None

        self.hp_text = None

        # TODO rename file
        # TODO first time sound is player, game lagg
        self.collect_coin_sound = arcade.load_sound("Sounds/beltHandle2.ogg")
        self.start_sound = arcade.load_sound("Sounds/prepare_yourself.ogg")
        self.win_sound = arcade.load_sound("Sounds/you_win.ogg")

        arcade.set_background_color(arcade.csscolor.BLACK)

    # TODO loading screen
    def setup(self):
        self.hero = Hero()

        self.level = Level(self.hero, TILE_NUM_X, TILE_NUM_Y)
        # self.level.set_up()

        # set up the game camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Stairs", use_spatial_hash=True)
        self.scene.add_sprite_list("Coins")
        self.scene.add_sprite_list("Player")

        self.coin_sprites = self.scene.get_sprite_list("Coins")

        # sets up the player, rendering at specific location
        player_texture = "Tiles/tile_0098.png"
        self.player_sprite = arcade.Sprite(player_texture, TILE_SCALING)
        self.player_sprite.center_x = self.hero.get_x() * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = self.hero.get_y() * TILE_SIZE + TILE_SIZE // 2
        self.scene.add_sprite("Player", self.player_sprite)

        # checks initial field of view
        # self.add_new_tiles(self.level.get_newly_visible_tiles())

        # tracks the time, of when the level was started
        self.start_time = time.time()

        # set up ui/ camera, extra so it does not move around like the rest of the game
        self.ui_camera = arcade.Camera(self.width, self.height)

        self.score_text = arcade.Text(f"Score: {self.score} / {NUM_COINS}", 8, SCREEN_HEIGHT - 24, arcade.csscolor.BLACK, 18)
        self.time_text = arcade.Text(f"Time: {self.start_time}", 8 + 5 * TILE_SIZE, SCREEN_HEIGHT - 24, arcade.csscolor.BLACK, 18)
        self.hp_text = arcade.Text(f"HP: {self.hero.get_hp()} / {self.hero.get_max_hp()}", 8 + 10 * TILE_SIZE, SCREEN_HEIGHT - 24,
                                   arcade.csscolor.GREEN, 18, bold=True)

        # TODO reduce big loading time
        # arcade.play_sound(self.start_sound, volume=0.5)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_change_x = 1

            if not DIAGONAL_MOVEMENT:
                self.player_change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_change_x = -1
            if not DIAGONAL_MOVEMENT:
                self.player_change_y = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player_change_y = 1
            if not DIAGONAL_MOVEMENT:
                self.player_change_x = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_change_y = -1
            if not DIAGONAL_MOVEMENT:
                self.player_change_x = 0

    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_change_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_change_x = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player_change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_change_y = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0 or past border
        if screen_center_x < 0:
            screen_center_x = 0
        elif screen_center_x > TILE_NUM_X * TILE_SIZE - SCREEN_WIDTH:
            screen_center_x = TILE_NUM_X * TILE_SIZE - SCREEN_WIDTH
        if screen_center_y < 0:
            screen_center_y = 0
        elif screen_center_y > TILE_NUM_Y * TILE_SIZE - SCREEN_HEIGHT:
            screen_center_y = TILE_NUM_Y * TILE_SIZE - SCREEN_HEIGHT + TILE_SIZE

        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def set_texture(self, texture, scene_name, x, y, t_scaling=TILE_SCALING):
        sprite = arcade.Sprite(texture, t_scaling)
        sprite.center_x = x * TILE_SIZE + TILE_SIZE // 2
        sprite.center_y = y * TILE_SIZE + TILE_SIZE // 2
        self.scene.add_sprite(scene_name, sprite)

    # TODO should not access maze here
    def add_new_tiles(self, new_tiles):
        if new_tiles is not None:
            for tile in new_tiles:
                x, y = tile
                # random walls and floor tiles to make it look nicer
                if self.level.maze(x, y) == "#":
                    wall_texture = choice(("Tiles/tile_0014.png", "Tiles/tile_0040.png"))
                    self.set_texture(wall_texture, "Walls", x, y)
                else:
                    floor_texture = choice(("Tiles/tile_0042.png", "Tiles/tile_0048.png", "Tiles/tile_0049.png"))
                    self.set_texture(floor_texture, "Floor", x, y)
                if self.level.maze(x, y) == "c":
                    coin = "Tiles/tile_0003.png"
                    self.set_texture(coin, "Coins", x, y, COIN_SCALING)
                # TODO better stair texture
                elif self.level.maze(x, y) == "S":
                    stair_texture = "Tiles/tile_0039.png"
                    self.set_texture(stair_texture, "Stairs", x, y)

    def update_hp_display(self):
        self.hp_text.text = f"HP: {self.hero.get_hp()} / {self.hero.get_max_hp()}"

    # TODO maybe do more dynamic, as in not = but +=
    def update_score(self, coins_collected):
        self.score = coins_collected
        self.score_text.text = f"Score: {self.score}"

    def update_display_time(self):
        self.time_text.text = f"Time: {round(time.time() - self.start_time, 1)}"

    def update_player_sprite(self):
        self.player_sprite.center_x = self.hero.get_x() * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = self.hero.get_y() * TILE_SIZE + TILE_SIZE // 2

    # def update_coin_sprites(self):
    #     for coin in self.coin_sprites:
    #         if self.last_collected_coin == (int(coin.center_x / TILE_SIZE), int(coin.center_y / TILE_SIZE)):
    #             self.coin_sprites.remove(coin)

    def remove_coin_sprite(self, coin_pos):
        for coin in self.coin_sprites:
            if coin_pos == (int(coin.center_x / TILE_SIZE), int(coin.center_y / TILE_SIZE)):
                self.coin_sprites.remove(coin)

    def update_sprites(self):
        self.update_player_sprite()
        # self.update_coin_sprites()
        # TODO insert enemy sprites

    def draw_ui(self):
        # used as a background to draw on
        arcade.draw_rectangle_filled(0, SCREEN_HEIGHT - TILE_SIZE / 2, SCREEN_WIDTH * 2, TILE_SIZE, arcade.csscolor.SADDLE_BROWN)
        self.score_text.draw()
        self.time_text.draw()
        self.hp_text.draw()

    # TODO should be in level, because of the maze, but how return condtion?
    def check_special_collision(self):
        cx, cy = self.hero.get_position()
        tile = self.level.maze(cx, cy)
        if tile != ".":
            if tile == "c":
                self.coins_collected += 1
                self.remove_coin_sprite((cx, cy))
            elif tile == "S":
                print("Oh boy, here we go again")
                self.level = Level(self.hero, TILE_NUM_X, TILE_NUM_Y)
                # TODO need to clear scene and rendering

    def on_draw(self):
        # clears the screen
        self.clear()

        # camera for main game
        self.camera.use()

        self.scene.draw()

        # camera for ui
        self.ui_camera.use()

        self.draw_ui()

    def update_things(self, delta_time):
        # updates player position
        self.level.move_player(self.player_change_x, self.player_change_y)

        self.check_special_collision()

        # adds new tiles to scene
        self.add_new_tiles(self.level.get_newly_visible_tiles())

        self.update_sprites()

        self.center_camera_to_player()

        # update ui, later, if more stuff, put in extra method
        self.update_hp_display()
        self.update_score(self.level.get_coins_collected())
        self.update_display_time()

        # TODO create hp view method


def main():
    window = Game()
    window.setup()
    # window.maze.print_out()

    arcade.schedule(window.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
