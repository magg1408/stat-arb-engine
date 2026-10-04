from dataclasses import dataclass 
from typing import Dict, Any

class Event:
    """Base Event class."""
    pass

@dataclass
class MarketEvent(Event):
    def __init__(self, timestamp, data=None, prices=None):
        self.type = 'MARKET'
        self.timestamp = timestamp
        # Handle positional or named inputs flexibly
        price_dict = data if data is not None else (prices if prices is not None else {})
        self.prices = price_dict
        self.data = price_dict  # Alias so strategy.py can read market_event.data
@dataclass
class SignalEvent(Event):
    def __init__(self, timestamp, pair, signal_type, z_score=0.0):
        self.type = 'SIGNAL'
        self.timestamp = timestamp
        self.pair = pair
        self.signal_type = signal_type
        self.z_score = z_score

@dataclass
class OrderEvent(Event):
    def __init__(self, timestamp, symbol, direction, quantity):
        self.type = 'ORDER'
        self.timestamp = timestamp
        self.symbol = symbol
        self.direction = direction
        self.action = direction       # Alias fallback
        self.order_type = direction   # Alias fallback
        self.quantity = quantity
@dataclass
class FillEvent(Event):
    def __init__(self, time, timestamp=None, symbol=None, exchange=None, quantity=None, direction=None, fill_price=0.0, fill_cost=None, commission=0.0, slippage=0.0, **kwargs):
        self.type = 'FILL'
        self.timestamp = timestamp or time
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        
        # Resolve price vs cost dynamically
        if fill_cost is not None and (fill_price == 0.0 or fill_price is None):
            self.fill_price = fill_cost
        else:
            self.fill_price = fill_price
            
        self.fill_cost = self.fill_price
        self.price = self.fill_price  # Fallback alias
        self.commission = commission
        self.slippage = slippage