class Weapon(Item):
    
    def __init__(self, damage, view):
        
        super().__init__()
        self._view = view
        
        self._damage = None
        
        self.set_damage(damage)
    
    #set position by class Item
    
    def set_damage(self, damage)
        if type(damage) == int:
            self._damage = damage
            return True
        return False
    
    def dropped(self, hero):
        hero.set_damage(hero.get_damage - self._damage)
    
    def picked_up(self, hero):
        hero.set_damage(hero.get_damage + self._damage)