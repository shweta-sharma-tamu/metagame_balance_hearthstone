class Minion:
    def __init__(self, name, attack, health, cost):
        self.name = name
        self.attack = attack
        self.health = health
        self.cost = cost

    def __str__(self):
        return f"Name: {self.name}, Cost: {self.cost}, Attack: {self.attack}, Health: {self.health}"


