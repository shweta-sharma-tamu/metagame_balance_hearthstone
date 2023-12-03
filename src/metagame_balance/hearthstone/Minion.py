class Minion:
    def __init__(self, name, attack, health, cost, rarity):
        self.name = name
        self.attack = attack
        self.health = health
        self.cost = cost
        self.rarity = rarity

    def __str__(self):
        return f"Name: {self.name}, Cost: {self.cost}, Attack: {self.attack}, Health: {self.health}, Rarity: {self.rarity}"
