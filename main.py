from queue import Queue
from data_handler import HistoricDataHandler
from strategy import PairsStatArbStrategy
from portfolio import Portfolio
from execution import SimulatedExecutionHandler
from analytics import calculate_performance_metrics, plot_equity_curve

def run_backtest():
    events = Queue()
    symbol_list = ["KO", "PEP"]
    
    data_handler = HistoricDataHandler(events, symbol_list, "2023-01-01", "2024-01-01")
    strategy = PairsStatArbStrategy(events, pair=('KO', 'PEP'), window=30)
    portfolio = Portfolio(events, initial_capital=100000.0)
    execution = SimulatedExecutionHandler(events)

    print("\n--- Running Event-Driven Backtest (KO vs PEP) ---\n")

    while data_handler.stream_next_bar():
        while not events.empty():
            event = events.get()

            if event.type == "MARKET":
                portfolio.update_market_price(event)
                strategy.calculate_signals(event)

            elif event.type == "SIGNAL":
                print(f"[{event.timestamp}] SIGNAL: {event.signal_type} | Z: {event.z_score:.2f}")
                portfolio.handle_signal(event)

            elif event.type == "ORDER":
                execution.execute_order(event, portfolio.latest_prices)

            elif event.type == "FILL":
                portfolio.update_fill(event)

    equity_df = portfolio.get_equity_df()
    metrics = calculate_performance_metrics(equity_df)
    plot_equity_curve(equity_df)

    print("\n================ STATISTICAL PERFORMANCE METRICS ================")
    print(f"Starting Capital : ${portfolio.initial_capital:,.2f}")
    print(f"Ending Equity    : ${equity_df['equity'].iloc[-1]:,.2f}")
    print(f"Total Return     : {metrics['Total Return (%)']:.2f}%")
    print(f"Sharpe Ratio     : {metrics['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown     : {metrics['Max Drawdown (%)']:.2f}%")
    print("=================================================================")

if __name__ == "__main__":
    run_backtest()