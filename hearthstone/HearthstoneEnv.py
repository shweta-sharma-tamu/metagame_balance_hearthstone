import random
from typing import Tuple

import gym
import numpy as np
from gym import spaces

# Define constants for the simplified Hearthstone environment
from Constants import MAX_HIT_POINTS, MAX_MANA, DEFAULT_N_ACTIONS

class HearthstoneEnv(gym.Env):
    def __init__(self, minion_player, minion_opponent):
        self.player_health = MAX_HIT_POINTS
        self.opponent_health = MAX_HIT_POINTS
        self.player_mana = MAX_MANA
        self.opponent_mana = MAX_MANA
        self.player_hand = np.array(minion_player, dtype=object)
        self.opponent_hand = np.array(minion_opponent, dtype=object)
        self.player_board = np.array([], dtype=object)
        self.opponent_board = np.array([], dtype=object)
        self.turn = 0
        self.winner = None

        self.action_space = spaces.Discrete(DEFAULT_N_ACTIONS)
        self.observation_space = spaces.MultiDiscrete([
            MAX_HIT_POINTS + 1,  # Player health
            MAX_HIT_POINTS + 1,  # Opponent health
            MAX_MANA + 1,  # Player mana
            MAX_MANA + 1,  # Opponent mana
            10,  # Maximum hand size
            10,  # Maximum board size
        ])

    def step(self, actions: Tuple[int, int]):
        # Validate the action inputs
        assert self.action_space.contains(actions[0])
        assert self.action_space.contains(actions[1])

        # Unpack actions
        player_action, target = actions

        # Player's turn
        if self.turn % 2 == 0:
            if player_action == 0:  # Play a card from hand to board
                if len(self.player_hand) > 0 and len(self.player_board) < 7:  # Check if hand is not empty and board is not full
                    played_card = self.player_hand[0]
                    self.player_hand = np.delete(self.player_hand, 0)  # Remove card from hand
                    self.player_board = np.append(self.player_board, played_card)  # Place card on board
                    self.player_mana -= played_card.cost  # Deduct mana cost
            elif player_action == 1 and len(self.player_board) > 0:  # Attack with a minion on the board
                if target < len(self.opponent_board):  # Check if the target exists on opponent's board
                    card = random.randint(0, len(self.player_board) - 1)
                    attacking_minion = self.player_board[card]
                    self.opponent_health -= attacking_minion.attack  # Reduce opponent's health
                    attacking_minion.health -= self.opponent_board[target].attack  # Simulate counter-attack
                    if attacking_minion.health <= 0:  # Remove minion if health drops to 0
                        self.player_board = np.delete(self.player_board, card)
            elif player_action == 2:  # Use hero power
                # Placeholder for hero power effect (if any)
                pass
            elif player_action == 3:  # End Turn
                self.turn += 1
                self.player_mana = min(self.player_mana + 1, MAX_MANA)  # Increment player's mana for the next turn

        # Opponent's turn (placeholder logic, simple random actions by the opponent)
        else:
            if len(self.opponent_board) == 0:
                opponent_action = 0
            elif len(self.opponent_hand) == 0:
                opponent_action = np.random.choice([1, 2, 3])
            elif len(self.opponent_board) != 0 and len(self.opponent_hand) != 0:
                opponent_action = random.choice(range(1,DEFAULT_N_ACTIONS))
            if opponent_action == 0 and len(self.opponent_hand) > 0 and len(self.opponent_board) < 7:
                played_card = self.opponent_hand[0]
                self.opponent_hand = np.delete(self.opponent_hand, 0)
                self.opponent_board = np.append(self.opponent_board, played_card)
                self.opponent_mana -= played_card.cost
            elif opponent_action == 1 and len(self.opponent_board) > 0:
                if len(self.player_board) > 0:
                    target = random.randint(0, len(self.player_board) - 1)
                    # choose opponent card
                    card = random.randint(0, len(self.opponent_board) - 1)
                    attacking_minion = self.opponent_board[card]
                    self.player_health -= attacking_minion.attack
                    attacking_minion.health -= self.player_board[target].attack
                    if attacking_minion.health <= 0:
                        self.opponent_board = np.delete(self.opponent_board, card)
            elif opponent_action == 2:
                # Placeholder for opponent's hero power usage
                pass
            elif opponent_action == 3:
                self.turn += 1
                self.opponent_mana = min(self.opponent_mana + 1, MAX_MANA)
            # print(f'opp: {opponent_action}')

        # Check if the game is finished
        finished = self.player_health <= 0 or self.opponent_health <= 0

        # Define reward based on the game state
        if finished:
            if self.player_health <= 0:
                reward = -1  # Player loses
            elif self.opponent_health <= 0:
                reward = 1  # Player wins
            else:
                reward = 0  # Draw
        else:
            reward = 0

        # Update observation
        observation = np.array([
            self.player_health, self.opponent_health,
            self.player_mana, self.opponent_mana,
            len(self.player_hand), len(self.player_board),
            len(self.opponent_hand), len(self.opponent_board)
        ])

        return observation, reward, finished, {}

    def reset(self, minion_player, minion_opponent):
        # Reset the game state to the initial state
        self.player_health = MAX_HIT_POINTS
        self.opponent_health = MAX_HIT_POINTS
        self.player_mana = MAX_MANA
        self.opponent_mana = MAX_MANA
        self.player_hand = np.array(minion_player, dtype=object)
        self.opponent_hand = np.array(minion_opponent, dtype=object)
        self.player_board = np.array([], dtype=object)
        self.opponent_board = np.array([], dtype=object)
        self.turn = 0
        self.winner = None
