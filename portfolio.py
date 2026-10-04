import pandas as pd

class Portfolio:
    """
    Tracks portfolio cash, positions, order sizing based on signals,
    and logs total daily portfolio equity.
    """
    def __init__(self, events_queue, initial_capital=100000.0):
        self.events_queue = events_queue
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        
        self.current_positions = {'XOM': 0, 'CVX': 0}
        self.latest_prices = {}
        
        self.total_commissions = 0.0
        self.total_slippage = 0.0
        self.equity_curve = []

    def _get_clean_price(self, price_data):
        if isinstance(price_data, dict):
            return float(price_data.get('close', price_data.get('price', 0.0)))
        return float(price_data)

    def update_market_price(self, market_event):
        """Updates internal prices and logs current total equity."""
        prices = getattr(market_event, 'data', getattr(market_event, 'prices', {}))
        for symbol, data in prices.items():
            self.latest_prices[symbol] = data

        holdings_value = 0.0
        for symbol, pos in self.current_positions.items():
            price = self._get_clean_price(self.latest_prices.get(symbol, 0.0))
            holdings_value += pos * price

        total_equity = self.current_cash + holdings_value
        timestamp = getattr(market_event, 'timestamp', getattr(market_event, 'time', None))

        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': total_equity
        })

    def handle_signal(self, signal_event, hedge_ratio=1.0):
        """Generates target orders based on SIGNAL events."""
        from events import OrderEvent

        signal_type = getattr(signal_event, 'signal_type', getattr(signal_event, 'type', None))
        timestamp = getattr(signal_event, 'timestamp', getattr(signal_event, 'time', None))

        base_qty = 100
        hedge_qty = int(base_qty * hedge_ratio)

        if signal_type == 'LONG':
            self.events_queue.put(OrderEvent(timestamp, 'XOM', 'BUY', base_qty))
            self.events_queue.put(OrderEvent(timestamp, 'CVX', 'SELL', hedge_qty))
        elif signal_type == 'SHORT':
            self.events_queue.put(OrderEvent(timestamp, 'XOM', 'SELL', base_qty))
            self.events_queue.put(OrderEvent(timestamp, 'CVX', 'BUY', hedge_qty))
        elif signal_type == 'EXIT':
            for sym, pos in self.current_positions.items():
                if pos > 0:
                    self.events_queue.put(OrderEvent(timestamp, sym, 'SELL', abs(pos)))
                elif pos < 0:
                    self.events_queue.put(OrderEvent(timestamp, sym, 'BUY', abs(pos)))

    def update_fill(self, fill_event):
        """Updates cash and position balances after receiving a FillEvent."""
        sym = fill_event.symbol
        direction = 1 if fill_event.direction == 'BUY' else -1
        
        raw_price = getattr(fill_event, 'fill_price', getattr(fill_event, 'price', 0.0))
        fill_price = self._get_clean_price(raw_price)
        fill_cost = fill_event.quantity * fill_price

        self.current_positions[sym] = self.current_positions.get(sym, 0) + (direction * fill_event.quantity)

        commission = getattr(fill_event, 'commission', 0.0)
        slippage = getattr(fill_event, 'slippage', 0.0)

        if fill_event.direction == 'BUY':
            self.current_cash -= (fill_cost + commission)
        else:
            self.current_cash += (fill_cost - commission)

        self.total_commissions += commission
        self.total_slippage += slippage