import numpy as np
import random
from Minion import Minion  # Import the Minion class from your module
from HearthstoneEnv import HearthstoneEnv  # Import the HearthstoneEnv class from your module
from loadMinion import loadMinionFromFile

def sim_env(num_game, max_turn, minion_player_list, minion_opponent_list, env):
    results = []
    for i in range(num_game):
        env.reset(minion_player_list, minion_opponent_list)
        for _ in range(max_turn):
            if (len(env.player_hand) == 0 and len(env.player_board) == 0) or (len(env.opponent_hand) == 0 and len(env.opponent_board) == 0):
                break
            if len(env.player_board) == 0:
                actions = (0, np.random.choice(np.arange(4)))
            elif len(env.player_hand) == 0 and len(env.player_board) > 0:
                if len(env.opponent_board) > 0:
                    actions = (np.random.choice([1, 2, 3]), np.random.choice(np.arange(len(env.opponent_board))))
                elif len(env.opponent_board) == 0:
                    actions = (np.random.choice([1, 2, 3]), 0)
            elif len(env.player_board) != 0 and len(env.player_hand) != 0:
                if len(env.opponent_board) > 0:
                    actions = (np.random.choice([1, 2, 3]), np.random.choice(np.arange(len(env.opponent_board))))
                elif len(env.opponent_board) == 0:
                    actions = (np.random.choice([1, 2, 3]), 0)
            observation, _, done, _ = env.step(actions)
        if observation[0] >= observation[1]:
            results.append(1)  # Player wins
        elif observation[0] < observation[1]:
            results.append(0)  # Opponent wins
    results = np.array(results)
    return len(results[results == 1]) / len(results)

if __name__ == "__main__":
    num_game, max_turn = 1000, 1000
    minion_list = loadMinionFromFile()
    minion_player_list = random.sample(minion_list, 30)
    minion_opponent_list = random.sample(minion_list, 30)
    env = HearthstoneEnv(minion_player_list, minion_opponent_list)
    
    win_rate = sim_env(num_game, max_turn, minion_player_list, minion_opponent_list, env)
    print(f"Win rate: {win_rate * 100:.2f}%")
