from item import Item


class Weapon(Item):
    def __init__(self, pos, damage):
        super().__init__(pos)
        self.damage = damage

    def __str__(self):
        return "W"

    def set_damage(self, damage):
        self.damage = damage

    def dropped(self, hero):
        hero.set_damage(hero.get_damage - self.damage)

    def collected(self, hero):
        hero.damage += self.damage
