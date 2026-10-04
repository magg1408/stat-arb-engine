import pandas as pd
from events import FillEvent, OrderEvent

class SimulatedExecutionHandler:
    """
    Simulates order execution by applying transaction costs, slippage, 
    and generating FillEvent objects to return to the event queue.
    """
    def __init__(self, events_queue, commission_per_share=0.005, flat_fee=1.0, slippage_per_share=0.01):
        self.events_queue = events_queue
        self.commission_per_share = commission_per_share
        self.flat_fee = flat_fee
        self.slippage_per_share = slippage_per_share

    def execute_order(self, order: OrderEvent, latest_prices: dict = None):
        """
        Executes an OrderEvent and pushes a FillEvent to the queue.
        Handles dictionary vs float price structures and variable direction attributes.
        """
        if latest_prices is None or order.symbol not in latest_prices or order.quantity == 0:
            return

        # 1. Safely extract numeric base price
        raw_price = latest_prices[order.symbol]
        if isinstance(raw_price, dict):
            base_price = float(raw_price.get('close', raw_price.get('price', 100.0)))
        else:
            base_price = float(raw_price)

        # 2. Extract direction regardless of attribute naming ('direction', 'order_type', or 'action')
        direction = getattr(order, 'direction', getattr(order, 'order_type', getattr(order, 'action', 'BUY')))

        # 3. Apply Slippage: Buys fill higher, Sells fill lower
        if str(direction).upper() == "BUY":
            fill_price = base_price + self.slippage_per_share
        else:
            fill_price = base_price - self.slippage_per_share

        # 4. Calculate Commissions & Transaction Costs
        commission = (order.quantity * self.commission_per_share) + self.flat_fee
        slippage_cost = order.quantity * self.slippage_per_share

        # 5. Build and dispatch FillEvent
        timestamp = getattr(order, 'timestamp', None)
        
        fill_event = FillEvent(
            timestamp=timestamp,
            time=timestamp,
            symbol=order.symbol,
            exchange='ARCA',
            quantity=order.quantity,
            direction=direction,
            fill_price=fill_price,
            commission=commission,
            slippage=slippage_cost
        )

        self.events_queue.put(fill_event)