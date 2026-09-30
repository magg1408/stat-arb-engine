import numpy as np

class KalmanHedgeFilter:
    """
    Online 2D Kalman Filter for dynamic linear regression tracking:
    Price_A = alpha + beta * Price_B + measurement_error
    """
    def __init__(self, delta=1e-4, R=1e-3):
        # State Vector [alpha, beta]^T initialized to zero
        self.state = np.zeros(2)
        
        # Covariance Matrix P initialized with high variance
        self.P = np.eye(2)
        
        # State Transition noise covariance W
        self.W = delta / (1 - delta) * np.eye(2)
        
        # Measurement noise variance R
        self.R = R

    def update(self, price_a: float, price_b: float):
        """
        Processes a new price observation pair (price_a = Y, price_b = X)
        and updates online estimates for alpha, beta, and prediction error (spread).
        """
        # Observation vector x_t = [1.0, price_b]
        x = np.array([1.0, price_b])

        # 1. Predict state and covariance
        self.P = self.P + self.W

        # 2. Compute Innovation / Measurement Residual (Spread)
        y_hat = np.dot(x, self.state)
        error = price_a - y_hat  # Current Spread

        # 3. Compute Innovation Covariance S
        S = np.dot(x, np.dot(self.P, x.T)) + self.R

        # 4. Compute Kalman Gain K
        K = np.dot(self.P, x.T) / S

        # 5. State & Covariance Update
        self.state = self.state + K * error
        self.P = self.P - np.outer(K, np.dot(x, self.P))

        alpha, beta = self.state[0], self.state[1]
        return alpha, beta, error, np.sqrt(S)