# Event-Driven Statistical Arbitrage & Backtesting Engine

An event-driven backtesting framework written in Python designed to backtest pairs trading and statistical arbitrage strategies with modular architecture and performance analytics.

## 📌 Features

- **Event-Driven Architecture**: Decouples data streaming (`MarketEvent`), strategy logic (`SignalEvent`), order routing (`OrderEvent`), and execution simulation (`FillEvent`).
- **Statistical Arbitrage Strategy**: Implements rolling $Z$-score mean-reversion pairs trading on cointegrated assets (KO / PEP).
- **Execution Simulation**: Tracks slippage, fill pricing, portfolio cash management, and position sizes.
- **Performance Analytics**: Calculates total return, maximum drawdown, annualized Sharpe ratio, and generates equity/drawdown charts.

## 🏗️ System Architecture

```text
+-----------------------+
|  HistoricDataHandler  | ---- (MarketEvent) ----> +--------------------+
+-----------------------+                         | PairsStatArbStrategy|
            |                                     +--------------------+
            |                                               |
            v                                         (SignalEvent)
+-----------------------+                                   |
|       Portfolio       | <---------------------------------+
+-----------------------+
  |                   ^
(OrderEvent)      (FillEvent)
  v                   |
+-----------------------+
| ExecutionHandler      |
+-----------------------+