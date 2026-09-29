from events import OrderEvent, FillEvent

class SimulatedExecutionHandler:
    """Simulates instantaneous order fills with zero slippage/commission."""
    def __init__(self, events_queue):
        self.events_queue = events_queue

    def execute_order(self, order: OrderEvent, latest_prices: dict):
        if order.symbol in latest_prices:
            fill_price = latest_prices[order.symbol]
            fill_event = FillEvent(
                timestamp=order.timestamp,
                symbol=order.symbol,
                quantity=order.quantity,
                direction=order.order_type,
                fill_cost=fill_price
            )
            self.events_queue.put(fill_event)