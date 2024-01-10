from character import Character

BASE_HP_LOSS = 0.005


class Hero(Character):
    def __init__(self, x=1, y=1, hp=20, damage=4):
        super().__init__(x, y, hp, damage)

    def __str__(self):
        return "H"

    def is_dead(self):
        return self.hp <= 0

    # TODO should the hero or the level change his hp? if level or items, do damage function

    def hp_decay(self, invincibility, levels_played):
        # Base + scaling
        if not invincibility:
            self.hp -= BASE_HP_LOSS + BASE_HP_LOSS * levels_played * 0.5
