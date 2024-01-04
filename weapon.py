from item import Item


class Weapon(Item):

    def __init__(self, x, y, damage):
        self.x_pos =  x
        self.y_pos = y
        self.damage = damage

    # set position by class Item

    def set_damage(self, damage):
        self.damage = damage

    def dropped(self, hero):
        hero.set_damage(hero.get_damage - self.damage)

    def collected(self, hero):
        hero.damage += self.damage
