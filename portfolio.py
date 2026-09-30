import pandas as pd
from events import SignalEvent, OrderEvent, FillEvent

class Portfolio:
    """
    Handles position sizing, order generation, cash accounting, 
    and transaction friction (commissions, slippage, borrow fees).
    """
    def __init__(self, events_queue, initial_capital=100000.0, allocation_per_trade=20000.0, short_borrow_rate=0.015):
        self.events_queue = events_queue
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.allocation_per_trade = allocation_per_trade
        self.short_borrow_rate = short_borrow_rate  # Annualized borrow rate (1.5%)
        
        self.positions = {'KO': 0, 'PEP': 0}
        self.latest_prices = {'KO': 0.0, 'PEP': 0.0}
        
        # Friction tracking
        self.total_commissions = 0.0
        self.total_slippage = 0.0
        self.total_borrow_fees = 0.0
        
        self.equity_curve = []

    def total_equity(self) -> float:
        """Calculates total portfolio equity."""
        position_value = sum(self.positions[sym] * self.latest_prices[sym] for sym in self.positions)
        return self.current_cash + position_value

    def update_market_price(self, market_event):
        """Updates internal price cache, deducts daily borrow fees, and logs daily equity."""
        for symbol in market_event.data:
            self.latest_prices[symbol] = market_event.data[symbol]['close']

        # Deduct daily short borrow cost on any short positions held overnight
        daily_borrow_cost = 0.0
        for sym, qty in self.positions.items():
            if qty < 0:  # Short position
                short_val = abs(qty) * self.latest_prices[sym]
                daily_borrow_cost += short_val * (self.short_borrow_rate / 365.0)

        self.current_cash -= daily_borrow_cost
        self.total_borrow_fees += daily_borrow_cost

        # Record daily equity snapshot
        current_val = self.total_equity()
        self.equity_curve.append({
            "timestamp": market_event.timestamp,
            "equity": current_val,
            "cash": self.current_cash
        })

    def handle_signal(self, signal: SignalEvent, hedge_ratio: float = 1.0):
        """Translates strategy signals into orders sized dynamically by hedge ratio (beta)."""
        stock_a, stock_b = signal.symbol_pair
        price_a = self.latest_prices[stock_a]
        price_b = self.latest_prices[stock_b]

        if price_a == 0 or price_b == 0:
            return

        # Sizing Leg A based on capital allocation, sizing Leg B using dynamic beta
        target_val_a = self.allocation_per_trade / 2.0
        qty_a = max(1, int(target_val_a / price_a))
        qty_b = max(1, int(qty_a * hedge_ratio))

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
        """Updates cash, position counts, and transaction cost logs."""
        trade_val = fill.quantity * fill.fill_cost
        
        if fill.direction == "BUY":
            self.positions[fill.symbol] += fill.quantity
            self.current_cash -= (trade_val + fill.commission)
        elif fill.direction == "SELL":
            self.positions[fill.symbol] -= fill.quantity
            self.current_cash += (trade_val - fill.commission)

        self.total_commissions += fill.commission
        self.total_slippage += fill.slippage

    def get_equity_df(self) -> pd.DataFrame:
        """Returns equity history as a DataFrame."""
        df = pd.DataFrame(self.equity_curve)
        df.set_index("timestamp", inplace=True)
        return df