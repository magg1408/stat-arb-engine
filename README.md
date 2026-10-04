# ⚡ Dynamic Event-Driven Statistical Arbitrage Engine

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Strategy](https://img.shields.io/badge/Strategy-Statistical%20Arbitrage-green.svg)
![Model](https://img.shields.io/badge/Model-Kalman%20Filter-orange.svg)
![Architecture](https://img.shields.io/badge/Architecture-Event--Driven-purple.svg)

A production-grade, event-driven backtesting and quantitative trading framework built in Python. Designed specifically for institutional equity pairs trading (**XOM / CVX**), this engine replaces traditional static lookback windows with dynamic online parameter estimation via a **Kalman Filter**.

The core loop strictly enforces event queue boundaries (`MARKET` ➔ `SIGNAL` ➔ `ORDER` ➔ `FILL`), eliminating lookahead bias while accounting for realistic market microstructure dynamics including bid-ask slippage and per-share commission structures.

---

## 🛠️ System Architecture

The modular framework decouples market data streaming, strategy logic, risk management, and order execution through standard FIFO queues:


## 🛠️ System Architecture

The modular framework decouples market data streaming, strategy logic, risk management, and order execution through standard FIFO queues:

```
                  ┌──────────────────────┐
                  │ HistoricDataHandler  │
                  └──────────┬───────────┘
                             │ (MARKET Event)
                             ▼
  ┌─────────────────┐   ┌─────────┐   ┌─────────────────┐
  │ PairsStatArb    ├──►│  Queue  │◄──┤ Portfolio       │
  │ Strategy        │   └────┬────┘   │ Manager         │
  └─────────────────┘        │        └─────────────────┘
        ▲ (MARKET)           │ (SIGNAL)        ▲ (FILL Event)
        └────────────────────┼─────────────────┘
                             │
                             ▼ (ORDER Event)
                  ┌──────────────────────┐
                  │ SimulatedExecution   │
                  │ Handler              │
                  └──────────────────────┘
```

### Component Breakdown
* **`events.py`**: Defines standard event interfaces (`MarketEvent`, `SignalEvent`, `OrderEvent`, `FillEvent`) with robust parameter aliases for multi-module compatibility.
* **`data_handler.py`**: Streams historical bar data sequentially into the pipeline, preventing future data leakage.
* **`kalman.py`**: Runs an online state-space Kalman Filter to dynamically track price beta and intercept.
* **`strategy.py`**: Evaluates normalized Z-score thresholds against real-time spread estimates to trigger long, short, or exit signals.
* **`portfolio.py`**: Manages portfolio cash, open inventory, beta-adjusted position sizing, and equity curve tracking.
* **`execution.py`**: Simulates exchange fills incorporating slippage models and multi-tier transaction costs.
* **`analytics.py`**: Computes performance metrics, tracks drawdowns, and outputs visual summary charts.

---

## 📐 Quantitative & Mathematical Methodology

### 1. Dynamic Hedge Ratio ($\beta_t$) Estimation
Rather than assuming a static cointegrating vector via standard Ordinary Least Squares (OLS), the dynamic hedge ratio is modeled as an adaptive state variable using a Kalman Filter:

$$\mathbf{y}_t = \mathbf{H}_t \boldsymbol{\theta}_t + \nu_t, \quad \nu_t \sim \mathcal{N}(0, R_t)$$
$$\boldsymbol{\theta}_t = \boldsymbol{\theta}_{t-1} + \boldsymbol{w}_t, \quad \boldsymbol{w}_t \sim \mathcal{N}(0, \mathbf{Q}_t)$$

* **Observation Vector ($\mathbf{y}_t$)**: Log price of target leg ($\text{XOM}$)
* **Measurement Matrix ($\mathbf{H}_t$)**: Matrix $[1, \text{log}(\text{CVX}_t)]$
* **State Vector ($\boldsymbol{\theta}_t$)**: $[\alpha_t, \beta_t]^T$ representing dynamic intercept and hedge ratio

### 2. Spread Dynamics & Z-Score Triggers
The residual spread $e_t$ is computed live and standardized using rolling moving statistics:

$$e_t = \text{Price}_{\text{XOM}} - \left(\beta_t \cdot \text{Price}_{\text{CVX}} + \alpha_t\right)$$

$$Z_t = \frac{e_t - \mu_e(N)}{\sigma_e(N)}$$

| Signal State | Condition | Trade Action |
| :--- | :--- | :--- |
| **Long Spread** | $Z_t \le -1.5$ | **BUY** XOM $\,$ / $\,$ **SELL** ($\beta_t \cdot \text{Qty}$) CVX |
| **Short Spread** | $Z_t \ge +1.5$ | **SELL** XOM $\,$ / $\,$ **BUY** ($\beta_t \cdot \text{Qty}$) CVX |
| **Exit Position** | $\Vert{}Z_t\Vert{} \le 0.0$ | Unwind open market positions across both legs |

---

## 💻 Microstructure & Execution Modeling

Real-world friction accounting is built into every execution fill:
* **Per-Share Fee**: \$0.005 per share
* **Flat Ticket Fee**: \$1.00 per order ticket
* **Slippage Model**: \$0.01 per share directional spread penalty

---

## 🚀 Quickstart Guide

### Installation
Clone the repository and install required runtime packages:

```bash
git clone [https://github.com/your-username/stat-arb-engine.git](https://github.com/your-username/stat-arb-engine.git)
cd stat-arb-engine
pip install pandas numpy matplotlib