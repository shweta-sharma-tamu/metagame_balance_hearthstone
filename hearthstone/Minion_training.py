class Minion_training:
    def __init__(self, attack, health, cost):
        self.attack = attack
        self.health = health
        self.cost = cost

    def __str__(self):
        return f"Cost: {self.cost}, Attack: {self.attack}, Health: {self.health}"