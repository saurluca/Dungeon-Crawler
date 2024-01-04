from item import Item

class Food(Item):
    def __init__(self, hp_restore):
        self.hp_restore = hp_restore

    def collected(self, hero):
        if hero.hp + self.hp_restore <= hero.max_hp:
            hero.hp += self.hp_restore
        else:
            hero.hp = hero.max_hp
