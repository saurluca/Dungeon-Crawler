import arcade
import time
from hero import Hero
from level import Level
from read_write import write_down_stats
from renderer import Renderer
from ui import UI

CHARACTER_SCALING = 1.8
TILE_SCALING = 2.0
COIN_SCALING = 1.4
ITEM_SCALING = 1.6
FOOD_SCALING = 1.5
TILE_SIZE = 32

# height should be width +1, to accommodate the ui
SCREEN_WIDTH = 19 * TILE_SIZE
SCREEN_HEIGHT = 20 * TILE_SIZE

# cheat mode for full vision
I_SEE_EVERYTHING = False
# no damage
I_AM_INVINCIBLE = False
# enables or disables diagonal movement
DIAGONAL_MOVEMENT = True
# enables sound files being loaded and played
SOUND_ON = True


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Dungeon Crawler")

        # keeps track of time spent in a level
        self.start_time = time.time()

        self.hero = Hero()

        self.renderer = Renderer()
        self.ui = UI(SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, self.start_time)

        self.level = None

        self.tick = 0
        self.player_is_dead = False

        # only odd numbers
        self.tile_num_x = 15
        self.tile_num_y = 15

        self.num_enemies = 0
        self.enemies_lst = []

        self.num_coins = 20
        self.total_num_coins = self.num_coins
        self.num_coins_collected = 0

        self.num_food = 2

        # used for interaction between level and main class
        self.player_change_x = 0
        self.player_change_y = 0

        # keeps track of number of levels played
        self.levels_played = 1

        if SOUND_ON:
            # TODO .wav or .ogg?
            self.coin_sound = arcade.load_sound("Sounds/coin_sound.wav")
            self.start_sound = arcade.load_sound("Sounds/prepare_yourself.ogg")
            self.win_sound = arcade.load_sound("Sounds/you_win.ogg")
            self.game_over_sound = arcade.load_sound("Sounds/dark-souls-you-died.wav")
            # self.food_sound = arcade.load_sound("")

        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        self.level = Level(self.hero, self.tile_num_x, self.tile_num_y, self.num_coins, self.num_food, self.num_enemies, self.enemies_lst)

        self.renderer.set_up(self.tile_num_x, self.tile_num_y, *self.hero.get_position())

        self.ui.set_up(self.hero.get_hp(), self.hero.get_max_hp(), self.num_coins_collected, self.total_num_coins, self.levels_played)

        # initial rendering of tiles in view, see everything, every tile, duh
        if I_SEE_EVERYTHING:
            every_tile = []
            for x in range(self.tile_num_x):
                for y in range(self.tile_num_y):
                    every_tile.append((x, y))
            self.renderer.add_new_tiles_to_scene(self.level.add_tile_type(every_tile))
        else:
            new_tiles = self.level.add_tile_type(self.level.get_newly_visible_tiles())
            self.renderer.add_new_tiles_to_scene(new_tiles)

        if SOUND_ON:
            arcade.play_sound(self.start_sound, volume=0.5)

    # if a key is pressed, changes movement speed in the pressed direction
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
        # finish game when pressing escape, save current stats
        elif key == arcade.key.ESCAPE:
            self.stop_game()

    # if key is released, resets movement speed in that direction
    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_change_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_change_x = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player_change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_change_y = 0

    # if player walks on stair, generates new level
    def advance_to_next_level(self):
        self.levels_played += 1
        self.ui.update_levels_played(self.levels_played)

        # TODO make distribution relative to total free tiles
        self.num_coins += self.levels_played * 2 + 3
        self.total_num_coins += self.num_coins
        self.num_food += self.levels_played * 2

        # only even numbers, so the end result will be odd
        self.tile_num_x += 2
        self.tile_num_y += 2
        self.setup()

    def stop_game(self):
        # write_down_stats(self.levels_played, round(time.time() - self.start_time, 1), self.num_coins_collected, self.total_num_coins)
        if SOUND_ON:
            arcade.play_sound(self.game_over_sound, volume=0.5)

        self.clear()
        arcade.draw_xywh_rectangle_filled(0, 0, SCREEN_HEIGHT, SCREEN_WIDTH, (00, 00, 00, 1))

        arcade.Text("YOU DIED", SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, arcade.csscolor.RED, 50).draw()
        arcade.finish_render()

        time.sleep(4)
        self.close()

    def on_draw(self):
        # clears the screen
        self.clear()

        self.renderer.draw_scene()

        self.ui.draw_ui()

    # noinspection PyUnusedLocal
    def update_things(self, delta_time):
        if self.tick % 2 == 0:
            # self.level.move_enemies()
            self.renderer.update_enemy_sprites(self.enemies_lst)

        # updates player position, if moved
        if self.player_change_x != 0 or self.player_change_y != 0:
            self.level.move_player(self.player_change_x, self.player_change_y)
            self.renderer.update_player_sprite(*self.hero.get_position())

            self.level.gameplay(I_AM_INVINCIBLE, self.levels_played)
            if self.level.check_completed():
                self.advance_to_next_level()

            self.renderer.center_camera_to_player()

            # adds new tiles to scene
            if not I_SEE_EVERYTHING:
                new_tiles = self.level.add_tile_type(self.level.get_newly_visible_tiles())
                self.renderer.add_new_tiles_to_scene(new_tiles)

            if self.level.check_item_collected():
                self.renderer.update_item_sprites(self.hero.get_position())

            if self.level.check_food_collected():
                self.renderer.update_food_sprites(self.hero.get_position())

            if self.level.check_coin_collected():
                self.num_coins_collected += 1
                self.renderer.update_coin_sprites(self.hero.get_position())
                self.ui.update_score(self.num_coins_collected, self.total_num_coins)
                if SOUND_ON:
                    arcade.play_sound(self.coin_sound, volume=0.5)

        self.ui.update_hp_display(self.hero.get_hp(), self.hero.get_max_hp())
        self.ui.update_display_time()
        self.level.reset_collected_status()

        self.tick += 1

        if self.player_is_dead:
            self.stop_game()


def main():
    start_time = time.time()
    game = Game()
    print(f"boot up time 1: {round(time.time() - start_time, 2)}")
    game.setup()
    print(f"boot up time 2: {round(time.time() - start_time, 2)}")
    # game.level.maze.print_out()

    arcade.schedule(game.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
