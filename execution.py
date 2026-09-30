from events import OrderEvent, FillEvent

class SimulatedExecutionHandler:
    """
    Simulates realistic market order execution with commissions and slippage.
    """
    def __init__(self, events_queue, commission_per_share=0.005, flat_fee=1.00, slippage_per_share=0.01):
        self.events_queue = events_queue
        self.commission_per_share = commission_per_share
        self.flat_fee = flat_fee
        self.slippage_per_share = slippage_per_share

    def execute_order(self, order: OrderEvent, latest_prices: dict):
        if order.symbol not in latest_prices or order.quantity == 0:
            return

        base_price = latest_prices[order.symbol]

        # 1. Slippage: Buys fill slightly higher, Sells fill slightly lower
        if order.order_type == "BUY":
            fill_price = base_price + self.slippage_per_share
        else:
            fill_price = base_price - self.slippage_per_share

        # 2. Commission: Per-share rate + flat order ticket fee
        commission = (order.quantity * self.commission_per_share) + self.flat_fee
        slippage_cost = order.quantity * self.slippage_per_share

        fill_event = FillEvent(
            timestamp=order.timestamp,
            symbol=order.symbol,
            quantity=order.quantity,
            direction=order.order_type,
            fill_cost=fill_price,
            commission=commission,
            slippage=slippage_cost
        )
        self.events_queue.put(fill_event)