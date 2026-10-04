import numpy as np
from events import SignalEvent
from kalman import KalmanHedgeFilter

class PairsStatArbStrategy:
    """
    Pairs Trading Strategy using Kalman Filter for dynamic hedge ratio estimation 
    and Z-Score threshold signals.
    """
    def __init__(self, events, pair=('XOM', 'CVX'), entry_z=1.0, exit_z=0.2):
        self.events = events
        self.pair = pair
        self.entry_z = entry_z
        self.exit_z = exit_z

        self.kalman = KalmanHedgeFilter(delta=1e-4, R=1e-3)
        self.price_cache = {pair[0]: None, pair[1]: None}

        self.in_position = False
        self.position_type = None  # 'LONG' or 'SHORT'
        self.current_beta = 1.0

    def calculate_signals(self, market_event):
        """
        Processes MarketEvent to calculate z-scores via Kalman filter and 
        emits SignalEvent objects when thresholds are breached.
        """
        prices = getattr(market_event, 'data', getattr(market_event, 'prices', {}))

        if self.pair[0] in prices and self.pair[1] in prices:
            val_a = prices[self.pair[0]]
            val_b = prices[self.pair[1]]

            # Extract numeric price if market_event contains dicts (e.g., {'close': 105.2})
            p1 = val_a['close'] if isinstance(val_a, dict) and 'close' in val_a else (val_a['price'] if isinstance(val_a, dict) else val_a)
            p2 = val_b['close'] if isinstance(val_b, dict) and 'close' in val_b else (val_b['price'] if isinstance(val_b, dict) else val_b)

            # Unpack only z_score and beta, ignoring additional returns
            z_score, beta, *rest = self.kalman.update(p1, p2)
            self.current_beta = beta
            # Signal Logic
            if not self.in_position:
                if z_score > self.entry_z:
                    # Spread is overvalued -> Short Spread (Short Asset A, Long Asset B)
                    print(f"[{market_event.timestamp}] SHORT SIGNAL | Z-Score: {z_score:.2f} | Beta: {beta:.2f}")
                    signal = SignalEvent(market_event.timestamp, self.pair, 'SHORT', z_score)
                    self.events.put(signal)
                    self.in_position = True
                    self.position_type = 'SHORT'

                elif z_score < -self.entry_z:
                    # Spread is undervalued -> Long Spread (Long Asset A, Short Asset B)
                    print(f"[{market_event.timestamp}] LONG SIGNAL | Z-Score: {z_score:.2f} | Beta: {beta:.2f}")
                    signal = SignalEvent(market_event.timestamp, self.pair, 'LONG', z_score)
                    self.events.put(signal)
                    self.in_position = True
                    self.position_type = 'LONG'

            else:
                # Exit logic when spread mean-reverts
                if (self.position_type == 'SHORT' and z_score <= self.exit_z) or \
                   (self.position_type == 'LONG' and z_score >= -self.exit_z):
                    print(f"[{market_event.timestamp}] EXIT SIGNAL | Z-Score: {z_score:.2f}")
                    signal = SignalEvent(market_event.timestamp, self.pair, 'EXIT', z_score)
                    self.events.put(signal)
                    self.in_position = False
                    self.position_type = None