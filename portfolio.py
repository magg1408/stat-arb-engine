import pandas as pd 
from events import SignalEvent, OrderEvent, FillEvent

class Portfolio:
    """Handles position sizing, order generation from signals, and portfolio equity/cash tracking with performance history."""
    def __init__(self, events_queue, initial_capital=100000.0, allocation_per_trade=20000.0):
        self.events_queue = events_queue
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.allocation_per_trade = allocation_per_trade

        self.positions = {'KO': 0, 'PEP': 0}
        self.latest_prices = {'KO': 0.0, 'PEP': 0.0}
        
        # History log for performance tracking
        self.equity_curve = []

    def update_market_price(self, market_event):
        """Updates internal price cache and logs daily portfolio value."""
        for symbol in market_event.data:
            self.latest_prices[symbol] = market_event.data[symbol]['close']

        # Record daily equity snapshot
        current_val = self.total_equity()
        self.equity_curve.append({
            "timestamp": market_event.timestamp,
            "equity": current_val,
            "cash": self.current_cash
        })

    def handle_signal(self, signal: SignalEvent):
        """Translates strategy signals into market orders."""
        stock_a, stock_b = signal.symbol_pair
        price_a = self.latest_prices[stock_a]
        price_b = self.latest_prices[stock_b]

        if price_a == 0 or price_b == 0:
            return

        qty_a = int((self.allocation_per_trade / 2) / price_a)
        qty_b = int((self.allocation_per_trade / 2) / price_b)

        if signal.signal_type == "SHORT_PAIR":
            self.events_queue.put(OrderEvent(signal.timestamp, stock_a, "SELL", qty_a))
            self.events_queue.put(OrderEvent(signal.timestamp, stock_b, "BUY", qty_b))

        elif signal.signal_type == "LONG_PAIR":
            self.events_queue.put(OrderEvent(signal.timestamp, stock_a, "BUY", qty_a))
            self.events_queue.put(OrderEvent(signal.timestamp, stock_b, "SELL", qty_b))

        elif signal.signal_type == "EXIT":
            if self.positions[stock_a] != 0:
                dir_a = "SELL" if self.positions[stock_a] > 0 else "BUY"
                self.events_queue.put(OrderEvent(signal.timestamp, stock_a, dir_a, abs(self.positions[stock_a])))
            
            if self.positions[stock_b] != 0:
                dir_b = "SELL" if self.positions[stock_b] > 0 else "BUY"
                self.events_queue.put(OrderEvent(signal.timestamp, stock_b, dir_b, abs(self.positions[stock_b])))

    def update_fill(self, fill: FillEvent):
        """Updates cash and position counts upon filled order."""
        if fill.direction == "BUY":
            self.positions[fill.symbol] += fill.quantity
            self.current_cash -= (fill.quantity * fill.fill_cost)
        elif fill.direction == "SELL":
            self.positions[fill.symbol] -= fill.quantity
            self.current_cash += (fill.quantity * fill.fill_cost)

    def total_equity(self) -> float:
        """Calculates total portfolio equity."""
        position_value = sum(self.positions[sym] * self.latest_prices[sym] for sym in self.positions)
        return self.current_cash + position_value

    def get_equity_df(self) -> pd.DataFrame:
        """Returns equity history as a DataFrame."""
        df = pd.DataFrame(self.equity_curve)
        df.set_index("timestamp", inplace=True)
        return df