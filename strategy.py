import numpy as np
import scipy.stats as stats
from events import SignalEvent

class PairsStatArbStrategy:
    """
    Rolling OLS Dynamic Hedge Ratio Pairs Trading Strategy.
    Calculates dynamic beta, spread, and rolling Z-score.
    """
    def __init__(self, events_queue, pair=('KO', 'PEP'), window=30, entry_z=2.0, exit_z=0.5):
        self.events_queue = events_queue
        self.pair = pair
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z

        self.price_history = {pair[0]: [], pair[1]: []}
        self.history_timestamps = []
        
        self.in_position = False
        self.position_type = None  # 'LONG_PAIR' or 'SHORT_PAIR'
        self.current_beta = 1.0

    def calculate_signals(self, market_event):
        """Processes market data, calculates dynamic beta & spread Z-score, emits signals."""
        for sym in self.pair:
            if sym in market_event.data:
                self.price_history[sym].append(market_event.data[sym]['close'])
        
        self.history_timestamps.append(market_event.timestamp)

        # Wait until we have enough lookback data
        if len(self.price_history[self.pair[0]]) < self.window:
            return

        # Slice rolling window
        prices_a = np.array(self.price_history[self.pair[0]][-self.window:])
        prices_b = np.array(self.price_history[self.pair[1]][-self.window:])

        # 1. Rolling OLS Regression: Price_A = alpha + beta * Price_B
        slope, intercept, _, _, _ = stats.linregress(prices_b, prices_a)
        self.current_beta = slope

        # 2. Compute Rolling Spread Series
        spread_series = prices_a - (self.current_beta * prices_b)
        current_spread = spread_series[-1]

        # 3. Calculate Spread Rolling Mean & Std Dev
        mean_spread = np.mean(spread_series)
        std_spread = np.std(spread_series)

        if std_spread == 0:
            return

        z_score = (current_spread - mean_spread) / std_spread
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
            # Exit on Mean Reversion
            if abs(z_score) < self.exit_z:
                self.in_position = False
                self.position_type = None
                self.events_queue.put(SignalEvent(timestamp, self.pair, 'EXIT', z_score))