import csv
import random
from Minion import Minion  # Import the Minion class from Minion.py

# Read data from CSV and filter minions with positive values for cost, attack, and health
minion_list = []

with open('cards.csv', newline='', encoding='latin-1') as csvfile:  # Change the encoding to 'latin-1'
    reader = csv.DictReader(csvfile)
    for row in reader:
        cost_str = row['cost']
        attack_str = row['attack']
        health_str = row['health']

        # Check for non-empty and numeric values
        if cost_str.isdigit() and attack_str.isdigit() and health_str.isdigit():
            cost = int(cost_str)
            attack = int(attack_str)
            health = int(health_str)

            if cost > 0 and attack > 0 and health > 0 and row['type'] == 'MINION':
                minion = Minion(row['name'], attack, health, cost)
                minion_list.append(minion)

# Select 5 random minions from the minion_list
random_minions = random.sample(minion_list, 5)

# Visualize the attributes of the selected minions
for minion in random_minions:
    print(minion)
