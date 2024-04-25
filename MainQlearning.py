"""
 Game Class: Central control unit for the 'Dungeon Crawler' game. Initializes core components,
such as the Hero, the graphical view, UI, renderer, and sound system. The Tick() function is the main game loop and
updates the game state
"""

import arcade
import time
from hero import Hero
from floor import Floor
from renderer import Renderer
from ui import UI
from qlearning import Agent, World, State  # from read_write import write_down_stats

TILE_SIZE = 32

# height should be width +2, to accommodate the ui
SCREEN_WIDTH = 19 * TILE_SIZE
SCREEN_HEIGHT = 21 * TILE_SIZE

# cheat mode for full vision
I_SEE_EVERYTHING = True
# cheat mode for no damage
I_AM_INVINCIBLE = False
# enemies will move and not just attack
MOVING_ENEMIES = False
# enemies will not be generated
GENERATE_ENEMIES = False
# False: game designed to hold down keys, True: game designed to tap keys
TAP_MOVEMENT_MODE = False


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Dungeon Crawler", center_window=True)
        # keeps track of time spent in a floor
        self.start_time = time.time()

        # initialises the hero with base values
        self.hero = Hero(hp=100, damage=4, armor=1, level=1)

        self.ui = UI(SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, self.start_time)

        self.renderer = None
        self.floor = None

        # difficulty: 0 No enemies, 1 standard, 2 hard, 3 blood sweat and tears
        self.difficulty = 0
        self.num_tick = 0
        self.on_floor = 0
        self.possible_score = 0

        # have to be odd, same value
        self.tile_num_x = 9
        self.tile_num_y = 9

        # instantiated as a list, so it has a pointer and can be changed in floor
        self.current_score = [0]

        self.hero_change_x = 0
        self.hero_change_y = 0

        # preloads the sound files to decrease loading time later
        self.start_sound = arcade.load_sound("Sounds/prepare_yourself.mp3")
        self.next_floor_sound = arcade.load_sound("Sounds/next_floor.mp3")
        self.you_died_sound = arcade.load_sound("Sounds/you_died.mp3")

        arcade.set_background_color(arcade.csscolor.BLACK)

        self.agent = None

    # this function sets up a new level every time the player finds the exit
    def set_up_new_instance(self):
        # short none audible sound to start up sound player
        if self.on_floor == 0:
            arcade.play_sound(self.start_sound)
        else:
            arcade.play_sound(self.next_floor_sound)

        # keeps track of the floor/ levels played
        self.on_floor += 1

        # increases floor size every 2 floors
        if self.on_floor % 2 == 0:
            self.tile_num_x += 2
            self.tile_num_y += 2

        # initializes the Floor, Renderer, and ui
        self.floor = Floor(self.hero, self.on_floor, self.difficulty, self.tile_num_x, self.tile_num_y, self.current_score, I_AM_INVINCIBLE,
                           GENERATE_ENEMIES)
        self.renderer = Renderer(self.tile_num_x, self.tile_num_y, *self.hero.get_position(), self.floor.enemy_lst, self.floor.uncovered_tiles)

        # Update the possible current_score the hero can achieve on this floor.
        self.possible_score += self.floor.points_on_floor

        # updates ui
        self.ui.update(self.hero, self.current_score, self.possible_score, self.on_floor)

        # initial rendering of tiles in view, if cheat mode see everything, uncovers every tile
        if I_SEE_EVERYTHING:
            beginning_tiles = self.uncover_everything(self.tile_num_x, self.tile_num_y)
        else:
            beginning_tiles = self.floor.add_tile_type(self.floor.get_newly_visible_tiles())
        self.renderer.add_new_tiles_to_scene(beginning_tiles)

        self.agent = Agent(self.floor.maze, self.hero, self.hero_change_x, self.hero_change_y)
        self.floor.maze.print_out()

    # uncovers every tile in the maze, because per default tiles not rendered
    def uncover_everything(self, tile_num_x, tile_num_y):
        every_tile = []
        for x in range(tile_num_x):
            for y in range(tile_num_y):
                every_tile.append((x, y))
        self.floor.uncovered_tiles = [[True for _ in range(tile_num_y)] for _ in range(tile_num_x)]
        return self.floor.add_tile_type(every_tile)

    # TODO Action
    def Action(self):
        pass

    def stop_game(self):
        # draws death screen
        self.clear()
        arcade.draw_xywh_rectangle_filled(0, 0, SCREEN_HEIGHT, SCREEN_WIDTH, (00, 00, 00, 1))
        arcade.Text("YOU DIED", SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, arcade.csscolor.RED, 50).draw()
        arcade.finish_render()

        arcade.play_sound(self.you_died_sound, volume=0.5)

        time.sleep(5)
        # write_down_stats(self.on_floor, round(time.time() - self.start_time, 1), self.num_coins_collected[0], self.possible_score)
        self.close()

    def on_draw(self):
        self.clear()

        self.renderer.draw_scene()

        self.ui.draw_ui()

    # noinspection PyUnusedLocal
    def update_things(self, delta_time):
        self.agent.Q_Learning_new()

        # moves the hero
        self.floor.move_hero(self.hero_change_x, self.hero_change_y)

        # reduces food of hero, and heals him at the cost of some food points if possible
        self.hero.food_decay(self.on_floor, I_AM_INVINCIBLE)
        self.hero.food_heal()

        # Update visibility of tiles, if fog of war is enabled
        if not I_SEE_EVERYTHING:
            new_tiles = self.floor.add_tile_type(self.floor.get_newly_visible_tiles())
            self.renderer.add_new_tiles_to_scene(new_tiles)

        if TAP_MOVEMENT_MODE:
            # in tap mode enemies attack every turn
            self.floor.enemies_attack()
            if MOVING_ENEMIES:
                # moves enemies if they are supposed to be moved
                self.floor.move_enemies()

        elif self.num_tick % 2 == 0:
            # normal movement mode, enemies attack every 2 ticks to balance them
            self.floor.enemies_attack()
            if MOVING_ENEMIES and self.num_tick % 4 == 0:
                # in normal movement mode, moves enemies every 4th turn, so they are not too fast
                self.floor.move_enemies()

        self.floor.update_enemy_visibility()
        self.renderer.update_enemy_sprites(self.floor.enemy_lst)

        # updates the renderer and the ui
        self.renderer.update(self.hero.pos)
        self.ui.update(self.hero, self.current_score, self.possible_score, self.on_floor)

        self.num_tick += 1

        # if floor completed, go to next floor/ make new instance of everything
        if self.floor.completed:
            self.set_up_new_instance()

        # if hero died, finish game
        if not self.hero.is_alive:
            self.stop_game()


def main():
    game = Game()
    game.set_up_new_instance()

    # TODO a.plot(episodes)
    # TODO a.showValues()

    # gets called every 1/8 of a second
    if not TAP_MOVEMENT_MODE:
        arcade.schedule(game.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
