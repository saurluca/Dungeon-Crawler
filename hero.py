from character import Character

BASE_HP_LOSS = 0.01


class Hero(Character):
    def __init__(self, x=1, y=1, hp=20, damage=4):
        super().__init__(x, y, hp, damage)

    def __str__(self):
        return "H"

    def is_dead(self):
        return self.hp <= 0
    # TODO should the hero or the level change his hp? if level or items, do damage function

    # TODO this means the hero only loses hp if he is moving. Okay?
    def hp_decay(self, invincibility, levels_played):
        if not invincibility:
            self.hp -= BASE_HP_LOSS * levels_played
