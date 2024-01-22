"""
 Game Class: Central control unit for the 'Dungeon Crawler' game. Initializes core components,
such as the Hero, the graphical view, UI, renderer, and sound system. The Tick() function is the main game loop and
updates the game state
"""

import time
from hero import Hero
from floor import Floor
from renderer import Renderer
from ui import UI
# from read_write import write_down_stats

# sets the scale of the game
TILE_SIZE = 16
NUM_TILES_X = 25
NUM_TILES_Y = 25
# plus 3 to have space for the UI
SCREEN_HEIGHT = (NUM_TILES_Y+3) * TILE_SIZE
SCREEN_WIDTH = NUM_TILES_X * TILE_SIZE


# cheat mode for full vision
I_SEE_EVERYTHING = False
# no damage
I_AM_INVINCIBLE = False


class Game:
    def __init__(self):
        self.start_time = time.time()

        # initialises the hero with base values
        self.hero = Hero(hp=100, damage=4, armor=1, level=1)

        # initialises the window (view) and the soundplayer
        self.view = SVGView(SCREEN_WIDTH, SCREEN_HEIGHT, "Dungeon Crawler")
        self.soundplayer = Soundplayer()

        self.ui = None
        self.renderer = None
        self.floor = None

        # difficulty: 0 No enemies, 1 standard, 2 hard, 3 blood sweat and tears
        self.difficulty = 1
        self.num_tick = 0
        self.on_floor = 0
        self.possible_score = 0

        # instantiated as a list, so it has a pointer and can be changed in floor
        self.current_score = [0]

    # this function sets up a new level every time the player finds the exit
    def set_up_new_instance(self):
        # short none audible sound to start up soundplayer
        if self.on_floor == 0:
            self.soundplayer.play("start")
        else:
            self.soundplayer.play("next_floor")

        # keeps track of the floor/ levels played
        self.on_floor += 1

        # initializes the Floor, Renderer, and ui
        self.floor = Floor(self.hero, self.on_floor, self.difficulty, NUM_TILES_X, NUM_TILES_Y, self.current_score, I_AM_INVINCIBLE)
        self.renderer = Renderer(self.view, NUM_TILES_X, NUM_TILES_Y)
        self.ui = UI(self.view, TILE_SIZE, NUM_TILES_X, NUM_TILES_Y, self.start_time, self.hero)

        # Update the possible current_score the hero can achieve on this floor.
        self.possible_score += self.floor.points_on_floor

        # updates the ui based on the current values
        self.ui.update(self.hero, self.current_score, self.possible_score, self.on_floor)

        # initial rendering of tiles in view, if cheat mode see everything, uncovers every tile
        if I_SEE_EVERYTHING:
            beginning_tiles = self.uncover_everything(NUM_TILES_X, NUM_TILES_Y)
        else:
            beginning_tiles = self.floor.add_tile_type(self.floor.get_newly_visible_tiles())
        self.renderer.add_new_tiles_to_scene(beginning_tiles)

        self.renderer.generate_hero_sprite(*self.hero.pos)
        self.renderer.generate_enemy_sprites(self.floor.enemy_lst)

    # uncovers every tile in the maze, because per default tiles not rendered
    def uncover_everything(self, tile_num_x, tile_num_y):
        every_tile = []
        for x in range(tile_num_x):
            for y in range(tile_num_y):
                every_tile.append((x, y))
        self.floor.uncovered_tiles = [[True for _ in range(tile_num_y)] for _ in range(tile_num_x)]
        return self.floor.add_tile_type(every_tile)

    # processes key presses to move hero
    # converts input to direction vector in x and y direction, default 0
    def process_key_press(self, key):
        if key == "ArrowRight" or key == "d":
            return 1, 0
        elif key == "ArrowLeft" or key == "a":
            return -1, 0
        elif key == "ArrowDown" or key == "s":
            return 0, 1
        elif key == "ArrowUp" or key == "w":
            return 0, -1

        elif key == "Escape":
            self.stop()
        return 0, 0

    # stops the game, rendering a death screen image and playing a sad sound :(
    def stop(self):
        self.renderer.death_screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.soundplayer.play("you_died")
        time.sleep(5)
        AlgoViz.clear()
        AlgoViz.hide()

    # this function updates the whole game whenever a key is pressed
    def tick(self):
        # Process input and move the hero in the resulting direction
        direction = self.process_key_press(self.view.wait_for_key())
        self.floor.move_hero(*direction)

        # reduces food of hero, and heals him at the cost of some food points if possible
        self.hero.food_decay(self.on_floor, I_AM_INVINCIBLE)
        self.hero.food_heal()

        # Update visibility of tiles, if fog of war is enabled
        if not I_SEE_EVERYTHING:
            new_tiles = self.floor.add_tile_type(self.floor.get_newly_visible_tiles())
            self.renderer.add_new_tiles_to_scene(new_tiles)

        # Manage enemy movement and visibility on the floor
        self.floor.move_enemies()
        self.floor.update_enemy_visibility()

        # Update the hero's position and render damage effects
        self.renderer.move_hero_sprite(*self.hero.get_position())
        self.renderer.render_hero_damaged(self.hero)

        # Handles the visuals when the hero collects something
        self.renderer.remove_collectable_sprite(self.floor.sprite_to_delete)

        # Update enemy sprites and render damage effects for enemies
        self.renderer.update_enemy_visibility(self.floor.enemy_lst)
        self.renderer.move_enemy_sprites(self.floor.enemy_lst)
        self.renderer.render_enemy_damaged(self.floor.enemy_lst)

        # Updates the user interface with the current game state
        self.ui.update(self.hero, self.current_score, self.possible_score, self.on_floor)

        # If the current floor is completed, set up the next floor
        if self.floor.completed:
            self.set_up_new_instance()

        # Check if the hero has died and end the game if so
        if not self.hero.is_alive:
            self.stop()
            return False

        # Return True to indicate the game should continue.
        return True
