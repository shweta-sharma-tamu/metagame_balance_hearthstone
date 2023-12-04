import cma
import numpy as np
import random
from Minion import Minion  # Import the Minion class from your module
from hearthstone_simulation import sim_env
from HearthstoneEnv import HearthstoneEnv
from Constants import NO_OF_GAMES, MAX_TURN 
from neuralnetwork import build_neural_network
from Minion_training import Minion_training
from loadMinion import loadMinionFromFile

# Define the objective function
def objective_function(card_selection):
    # Convert flat card_selection to a list of Minion objects
    minion_player_list = [Minion_training(*card_selection[i:i+3]) for i in range(0, 30 * 3, 3)]
    minion_opponent_list = [Minion_training(*card_selection[i:i+3]) for i in range(30 * 3, 60 * 3, 3)]

    env = HearthstoneEnv(minion_player_list, minion_opponent_list)
    # Simulate the environment and return the win rate
    win_rate = sim_env(NO_OF_GAMES, MAX_TURN, minion_player_list, minion_opponent_list, env)
    return 1-abs(0.5-win_rate)



# Define the combined objective function
def combined_objective_function(card_selection):
    # Convert flat card_selection to a list of Minion objects
    
    minion_player_list = [Minion_training(*card_selection[i:i+3]) for i in range(0, 30 * 3, 3)]
    minion_opponent_list = [Minion_training(*card_selection[i:i+3]) for i in range(30 * 3, 60 * 3, 3)]

    # Use the neural network to predict the probability distribution
    predicted_probabilities = neural_network.predict(np.array([card_selection]))[0]

    # Call the objective function with the appropriate arguments
    objective_func_value = objective_function(card_selection)

    # Add regularization term
    return objective_func_value + 0.1 * (1 - np.max(predicted_probabilities))



if __name__ == "__main__":
    # sample 100 from 1094 card list for demonstration purposes
    minion_list = loadMinionFromFile()
    random_minions = random.sample(minion_list, 100)
    vec = [[minion.attack, minion.health, minion.cost] for minion in random_minions]
    flatten_vec = [feature for sublist in vec for feature in sublist]

    num_samples = 1000
    input_dim = 100 * 3  # Assuming each Minion has 3 attributes (attack, health, cost)
    output_dim = 100  # Output represents the probability of selecting each card

    X_train = np.zeros((num_samples, input_dim))
    X_train[:,:] = flatten_vec
    y_train = np.zeros((num_samples, output_dim))

    # # Each row in y_train corresponds to the probability distribution over cards for a single sample
    for i in range(num_samples):
        selected_indices = random.sample(range(output_dim), 30)  # Select 30 cards out of 100 randomly
        y_train[i, selected_indices] = 1.0

    # Build and compile the neural network
    neural_network = build_neural_network(input_dim, output_dim)
    neural_network.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train the neural network
    neural_network.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=2)


    # Initialize CMA-ES optimizer
    initial_mean = np.random.rand(input_dim)
    es = cma.CMAEvolutionStrategy(initial_mean, 0.5)
    result = []
    # Optimization loop
    for iteration in range(100):
        # Generate samples
        solutions = es.ask()

        # Evaluate objective function
        fitness_values = [combined_objective_function(solution) for solution in solutions]

        # Update CMA-ES
        es.tell(solutions, fitness_values)

        # Train neural network with the best solution
        best_solution = solutions[np.argmin(fitness_values)]
        x_train = np.array([best_solution])
        y_train = np.zeros((1, output_dim))
        selected_indices = [i for i in range(output_dim) if best_solution[i] > 0.5]  # Threshold for selection
        y_train[0, selected_indices] = 1.0
        neural_network.fit(x_train, y_train, epochs=1, verbose=0)
        result.append(np.mean(neural_network.predict(x_train)))
        # Print progress
        print(f"Iteration {iteration + 1}, Mean Probability: {result[-1]}")

    # Get the best solution
    best_solution = es.result.xbest
    print("Best Card Selection:", best_solution)