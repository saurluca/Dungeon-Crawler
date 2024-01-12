import arcade
import time
from hero import Hero
from level import Level
from read_write import write_down_stats
from renderer import Renderer
from ui import UI

TILE_SIZE = 32

# height should be width +1, to accommodate the ui
SCREEN_WIDTH = 19 * TILE_SIZE
SCREEN_HEIGHT = 20 * TILE_SIZE

# cheat mode for full vision
I_SEE_EVERYTHING = True
# no damage
I_AM_INVINCIBLE = False
# enables or disables diagonal movement
DIAGONAL_MOVEMENT = True
# enables sound files being loaded and played
SOUND_ON = True


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Dungeon Crawler", center_window=True)
        # # fullscreen = True
        # width, height = self.get_size()
        # self.set_viewport(0, width, 0, height)

        # keeps track of time spent in a level
        self.start_time = time.time()

        self.hero = Hero()

        self.ui = UI(SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, self.start_time)

        self.renderer = None
        self.level = None

        self.tick = 0
        self.levels_played = 0

        self.total_num_coins = 0
        self.num_coins_collected = [0]

        # used for interaction between level and main class
        self.hero_change_x = 0
        self.hero_change_y = 0

        # preloads the sound files to decrease loading time later
        if SOUND_ON:
            # TODO decision: which file format?
            self.coin_sound = arcade.load_sound("Sounds/coin_sound.wav")
            self.start_sound = arcade.load_sound("Sounds/prepare_yourself.ogg")
            self.win_sound = arcade.load_sound("Sounds/you_win.ogg")
            self.game_over_sound = arcade.load_sound("Sounds/dark-souls-you-died.wav")
            self.food_sound = arcade.load_sound("Sounds/nom-nom-nom_s.mp3")

        arcade.set_background_color(arcade.csscolor.BLACK)

    def set_up_new_instance(self):
        self.levels_played += 1

        # first value is start size, second increment. total has to be odd
        tile_num_x = 15 + self.levels_played * 2
        tile_num_y = 15 + self.levels_played * 2

        # TODO decision: coins collected saved in hero, main, or level

        self.level = Level(self.hero, tile_num_x, tile_num_y, self.num_coins_collected)
        self.total_num_coins += self.level.num_coins
        self.renderer = Renderer(tile_num_x, tile_num_y, *self.hero.get_position(), self.level.enemy_lst, self.level.uncovered_tiles)
        self.ui.update(self.hero.get_hp(), self.hero.get_max_hp(), self.num_coins_collected, self.total_num_coins, self.levels_played)

        # how chosen what to look at
        # initial rendering of tiles in view, see everything, every tile, duh
        if I_SEE_EVERYTHING:
            beginning_tiles = self.uncover_everything(tile_num_x, tile_num_y)
        else:
            beginning_tiles = self.level.add_tile_type(self.level.get_newly_visible_tiles())
        self.renderer.add_new_tiles_to_scene(beginning_tiles)

        if SOUND_ON:
            arcade.play_sound(self.start_sound, volume=0.5)

    def uncover_everything(self, tile_num_x, tile_num_y):
        every_tile = []
        for x in range(tile_num_x):
            for y in range(tile_num_y):
                every_tile.append((x, y))
        self.level.uncovered_tiles = [[True for _ in range(tile_num_y)] for _ in range(tile_num_x)]
        return self.level.add_tile_type(every_tile)

    # if a key is pressed, changes movement speed in the pressed direction
    def on_key_press(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.hero_change_x = 1
            if not DIAGONAL_MOVEMENT:
                self.hero_change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.hero_change_x = -1
            if not DIAGONAL_MOVEMENT:
                self.hero_change_y = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.hero_change_y = 1
            if not DIAGONAL_MOVEMENT:
                self.hero_change_x = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.hero_change_y = -1
            if not DIAGONAL_MOVEMENT:
                self.hero_change_x = 0
        # finish game when pressing escape, save current stats
        elif key == arcade.key.ESCAPE:
            self.stop_game()

    # if key is released, resets movement speed in that direction
    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.hero_change_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.hero_change_x = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.hero_change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.hero_change_y = 0

    def stop_game(self):
        # draws death screen
        self.clear()
        arcade.draw_xywh_rectangle_filled(0, 0, SCREEN_HEIGHT, SCREEN_WIDTH, (00, 00, 00, 1))
        arcade.Text("YOU DIED", SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, arcade.csscolor.RED, 50).draw()
        arcade.finish_render()

        if SOUND_ON:
            arcade.play_sound(self.game_over_sound, volume=0.5)

        time.sleep(4)
        # write_down_stats(self.levels_played, round(time.time() - self.start_time, 1), self.num_coins_collected[0], self.total_num_coins)
        self.close()

    def on_draw(self):
        self.clear()

        self.renderer.draw_scene()

        self.ui.draw_ui()

    # noinspection PyUnusedLocal
    def update_things(self, delta_time):
        # updates the hero
        self.level.move_hero(self.hero_change_x, self.hero_change_y)
        self.hero.hp_decay(I_AM_INVINCIBLE, self.levels_played)

        # if fog of war on, add newly uncovered tiles to scene
        if not I_SEE_EVERYTHING:
            new_tiles = self.level.add_tile_type(self.level.get_newly_visible_tiles())
            self.renderer.add_new_tiles_to_scene(new_tiles)

        # updates enemies every 4th tick
        if self.tick % 4 == 0:
            self.level.move_enemies()
            self.renderer.update_enemy_sprites(self.level.enemy_lst)
        self.level.update_enemy_visibility()

        # updates the renderer and the ui
        self.renderer.update(self.hero.get_position())
        self.ui.update(self.hero.get_hp(), self.hero.get_max_hp(), self.num_coins_collected, self.total_num_coins, self.levels_played)

        # plays coin sound, if coin collected
        if SOUND_ON:
            if self.level.check_coin_collected():
                arcade.play_sound(self.coin_sound, volume=0.5)
            if self.level.check_food_collected():
                arcade.play_sound(self.food_sound, volume=0.5)

        self.tick += 1

        # if level completed, go to next level/ make new instance of everything
        if self.level.completed:
            self.set_up_new_instance()

        # if hero died, finish game
        if self.hero.is_dead():
            self.stop_game()


def main():
    # start_time = time.time()
    game = Game()
    # print(f"boot up time 1: {round(time.time() - start_time, 2)}")
    game.set_up_new_instance()
    # print(f"boot up time 2: {round(time.time() - start_time, 2)}")
    # game.level.maze.print_out()

    # gets called every 1/8 of a second
    arcade.schedule(game.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
