import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from sklearn.preprocessing import StandardScaler
import numpy as np

def build_autoencoder(input_dim):
    """
    Build an Autoencoder model.

    Args:
        input_dim (int): Number of input features.

    Returns:
        Model: Compiled Autoencoder model.
    """
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(16, activation='relu')(input_layer)
    encoded = Dense(8, activation='relu')(encoded)
    decoded = Dense(16, activation='relu')(encoded)
    output_layer = Dense(input_dim, activation='linear')(decoded)
    return Model(inputs=input_layer, outputs=output_layer)

def train_autoencoder(data):
    """
    Train the Autoencoder on the given data.

    Args:
        data (numpy.ndarray): Input data for training.

    Returns:
        tuple: Trained Autoencoder model and StandardScaler instance.
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(data)

    model = build_autoencoder(X.shape[1])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, X, epochs=50, batch_size=16, shuffle=True)

    # Save model for later use
    model.save("autoencoder_model.keras")
    return model, scaler

def detect_anomalies_with_autoencoder(data, model, scaler, threshold=0.01):
    """
    Detect anomalies using the trained Autoencoder.

    Args:
        data (numpy.ndarray): Input data for anomaly detection.
        model (Model): Trained Autoencoder model.
        scaler (StandardScaler): Scaler used during training.
        threshold (float): Reconstruction error threshold for anomalies.

    Returns:
        numpy.ndarray: Boolean array indicating anomalies.
    """
    X = scaler.transform(data)
    reconstructed = model.predict(X)
    reconstruction_error = np.mean(np.power(X - reconstructed, 2), axis=1)
    return reconstruction_error > threshold