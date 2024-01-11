from character import Character

BASE_HP_LOSS = 0.005


class Hero(Character):
    def __init__(self, pos=(1, 1), hp=20, damage=4):
        super().__init__(pos, hp, damage)

    def __str__(self):
        return "H"

    def is_dead(self):
        return self.hp <= 0

    def hp_decay(self, invincibility, levels_played):
        # Base + scaling
        if not invincibility:
            self.hp -= BASE_HP_LOSS + BASE_HP_LOSS * levels_played * 0.5

    def heal(self, value):
        self.hp = min(self.hp + value, self.max_hp)
