from tensorflow import keras
from tensorflow.keras import layers

# Build the neural network to predict card selection
def build_neural_network(input_dim, output_dim):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(output_dim, activation='sigmoid')
    ])
    return model