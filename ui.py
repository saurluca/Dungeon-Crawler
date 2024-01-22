import arcade
import time


class UI:
    def __init__(self, screen_height, screen_width, tile_size, start_time):
        self.ui_camera = arcade.Camera()

        self.tile_size = tile_size
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.start_time = start_time

        self.hp_text = arcade.Text("", 8, screen_height - 28, arcade.csscolor.GREEN, 18, bold=True)
        self.score_text = arcade.Text("", 8 + 5 * tile_size + 16, screen_height - 28, arcade.csscolor.BLACK, 18)
        self.on_floor = arcade.Text("", 8 + 10 * tile_size + 16, screen_height - 28, arcade.csscolor.BLACK, 18)
        self.time_text = arcade.Text("", 8 + 13 * tile_size + 16, screen_height - 28, arcade.csscolor.BLACK, 18)

        self.food_text = arcade.Text("", 8, screen_height - 56, arcade.csscolor.DARK_RED, 18, bold=True)
        self.damage_text = arcade.Text("", 8 + 4 * tile_size + 16, screen_height - 56, arcade.csscolor.BLACK, 18)
        self.armor_text = arcade.Text("", 8 + 7 * tile_size + 16, screen_height - 56, arcade.csscolor.BLACK, 18)

        self.level_text = arcade.Text("", 8 + 10 * tile_size + 16, screen_height - 56, arcade.csscolor.BLACK, 18)
        self.xp_text = arcade.Text("", 8 + 13 * tile_size, screen_height - 56, arcade.csscolor.BLACK, 18)

    def update(self, hero, current_score, possible_score, on_floor):
        self.update_hp_display(hero.hp, hero.max_hp)
        self.update_score(current_score[0], possible_score)
        self.update_on_floor(on_floor)
        self.update_display_time()

        self.update_food_text(hero.food_points, hero.max_food_points)
        self.update_level_text(hero.level)
        self.update_xp_text(hero.current_xp, hero.xp_to_next_level[hero.level])
        self.update_damage_text(hero.damage)
        self.update_armor_text(hero.armor)

    def update_hp_display(self, hero_hp, hero_max_hp):
        self.hp_text.text = f"HP: {int(hero_hp)} / {hero_max_hp}"

    def update_score(self, current_score, possible_score):
        self.score_text.text = f"Score: {current_score} / {possible_score}"

    def update_on_floor(self, on_floor):
        self.on_floor.text = f"Floor: {on_floor}"

    def update_display_time(self):
        self.time_text.text = f"Time: {round(time.time() - self.start_time, 1)}"

    def update_food_text(self, current_food, max_food):
        self.food_text.text = f"Food: {int(current_food)} / {max_food}"

    def update_level_text(self, level):
        self.level_text.text = f"Lvl: {level}"

    def update_xp_text(self, current_xp, xp_to_next_level):
        self.xp_text.text = f"XP: {current_xp} / {xp_to_next_level}"

    def update_damage_text(self, damage):
        self.damage_text.text = f"Dmg: {damage}"

    def update_armor_text(self, armor):
        self.armor_text.text = f"Arm: {armor}"

    # background square and text for score, time and hp displayed on the top
    def draw_ui(self):
        self.ui_camera.use()

        # used as a background to draw on
        arcade.draw_rectangle_filled(0, self.screen_height - self.tile_size / 2, self.screen_width * 2, self.tile_size * 3,
                                     arcade.csscolor.SADDLE_BROWN)

        self.hp_text.draw()
        self.score_text.draw()
        self.on_floor.draw()
        self.time_text.draw()

        self.food_text.draw()
        self.damage_text.draw()
        self.armor_text.draw()
        self.level_text.draw()
        self.xp_text.draw()
