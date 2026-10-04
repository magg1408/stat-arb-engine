import queue
from data_handler import HistoricDataHandler
from strategy import PairsStatArbStrategy
from portfolio import Portfolio
from execution import SimulatedExecutionHandler
from analytics import plot_equity_curve

def run_backtest():
    events = queue.Queue()
    
    symbols = ['XOM', 'CVX']
    data_handler = HistoricDataHandler(
        events_queue=events,
        symbol_list=symbols,
        start_date='2023-01-01',
        end_date='2024-01-01'
    )
    
    strategy = PairsStatArbStrategy(events)
    portfolio = Portfolio(events)
    execution = SimulatedExecutionHandler(events)

    # Main Event Loop
    while data_handler.stream_next_bar():
        while not events.empty():
            event = events.get()

            if event.type == 'MARKET':
                portfolio.update_market_price(event)
                strategy.calculate_signals(event)

            elif event.type == 'SIGNAL':
                portfolio.handle_signal(event, hedge_ratio=strategy.current_beta)

            elif event.type == 'ORDER':
                execution.execute_order(event, portfolio.latest_prices)

            elif event.type == 'FILL':
                portfolio.update_fill(event)

    # Generate performance chart after backtest completion
    plot_equity_curve(portfolio)

if __name__ == "__main__":
    run_backtest()