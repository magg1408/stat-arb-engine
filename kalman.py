import numpy as np

class KalmanHedgeFilter:
    def __init__(self, delta=1e-4, R=1e-3):
        self.delta = delta
        self.R = R
        self.W = delta * np.eye(2)
        
        # State vector [intercept, slope (beta)]
        self.state = np.zeros(2)
        self.P = np.zeros((2, 2))
        
        self.spread_history = []
        self.initialized = False

    def update(self, price_a: float, price_b: float):
        price_a = float(price_a)
        price_b = float(price_b)
        
        # Observation matrix X = [1.0, price_b]
        x = np.array([1.0, price_b])

        # Initialize baseline on first tick
        if not self.initialized:
            self.state[1] = price_a / price_b if price_b != 0 else 1.0
            self.initialized = True

        # Predict State & Covariance
        self.P = self.P + self.W

        # Compute Measurement Innovation / Error
        y_hat = np.dot(x, self.state)
        e = price_a - y_hat

        # Measurement Variance & Kalman Gain
        Q = np.dot(x, np.dot(self.P, x.T)) + self.R
        K = np.dot(self.P, x.T) / Q

        # State & Covariance Update
        self.state = self.state + K * e
        self.P = self.P - np.outer(K, np.dot(x, self.P))

        # Track Spread for Z-Score Calculation
        beta = self.state[1]
        spread = e
        self.spread_history.append(spread)

        # Rolling Z-Score Calculation (30-period window)
        window = 30
        if len(self.spread_history) > window:
            recent_spreads = self.spread_history[-window:]
            mean = np.mean(recent_spreads)
            std = np.std(recent_spreads)
            z_score = (spread - mean) / std if std != 0 else 0.0
        else:
            z_score = 0.0

        return z_score, beta