import numpy as np
from events import SignalEvent
from kalman import KalmanHedgeFilter

class PairsStatArbStrategy:
    """
    Kalman Filter Dynamic Hedge Ratio Pairs Strategy.
    Continuously updates state space estimates for alpha, beta, and spread Z-score.
    """
    def __init__(self, events_queue, pair=('KO', 'PEP'), entry_z=2.0, exit_z=0.5):
        self.events_queue = events_queue
        self.pair = pair
        self.entry_z = entry_z
        self.exit_z = exit_z

        self.kalman = KalmanHedgeFilter(delta=1e-4, R=1e-3)
        self.price_cache = {pair[0]: None, pair[1]: None}
        
        self.in_position = False
        self.position_type = None
        self.current_beta = 1.0

    def calculate_signals(self, market_event):
        """Updates Kalman Filter state on new price data and emits signals."""
        for sym in self.pair:
            if sym in market_event.data:
                self.price_cache[sym] = market_event.data[sym]['close']

        # Ensure both stock prices are loaded
        if self.price_cache[self.pair[0]] is None or self.price_cache[self.pair[1]] is None:
            return

        price_a = self.price_cache[self.pair[0]]
        price_b = self.price_cache[self.pair[1]]

        # Update Kalman Filter
        alpha, beta, spread, spread_std = self.kalman.update(price_a, price_b)
        self.current_beta = beta

        if spread_std == 0:
            return

        # Kalman Standardized Residual (Z-score)
        z_score = spread / spread_std
        timestamp = market_event.timestamp

        # Signal Logic
        if not self.in_position:
            if z_score <= -self.entry_z:
                self.in_position = True
                self.position_type = 'LONG_PAIR'
                self.events_queue.put(SignalEvent(timestamp, self.pair, 'LONG_PAIR', z_score))

            elif z_score >= self.entry_z:
                self.in_position = True
                self.position_type = 'SHORT_PAIR'
                self.events_queue.put(SignalEvent(timestamp, self.pair, 'SHORT_PAIR', z_score))

        else:
            if abs(z_score) < self.exit_z:
                self.in_position = False
                self.position_type = None
                self.events_queue.put(SignalEvent(timestamp, self.pair, 'EXIT', z_score))