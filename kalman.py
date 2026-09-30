import numpy as np

class KalmanHedgeFilter:
    """
    Online 2D Kalman Filter for dynamic linear regression tracking:
    Price_A = alpha + beta * Price_B + measurement_error
    """
    def __init__(self, delta=1e-3, R=1e-1):
        # State Vector [alpha, beta]^T
        self.state = np.zeros(2)
        
        # State Covariance Matrix P initialized with high initial uncertainty
        self.P = np.ones((2, 2)) * 10.0
        
        # Process Noise Covariance Matrix W
        self.W = delta * np.eye(2)
        
        # Measurement Noise Variance R
        self.R = R
        self.initialized = False

    def update(self, price_a: float, price_b: float):
        x = np.array([1.0, price_b])

        # Initialize baseline on first tick
        if not self.initialized:
            self.state[1] = price_a / price_b if price_b != 0 else 1.0
            self.initialized = True

        # Predict State & Covariance
        self.P = self.P + self.W

        # Compute Measurement Innovation / Error
        y_hat = np.dot(x, self.state)
        error = price_a - y_hat

        # Compute Innovation Variance S
        S = np.dot(x, np.dot(self.P, x.T)) + self.R

        # Compute Kalman Gain K
        K = np.dot(self.P, x.T) / S

        # State & Covariance Update
        self.state = self.state + K * error
        self.P = self.P - np.outer(K, np.dot(x, self.P))

        alpha, beta = self.state[0], self.state[1]
        spread_std = np.sqrt(S)

        return alpha, beta, error, spread_std