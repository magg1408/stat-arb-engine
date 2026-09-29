# Event-Driven Statistical Arbitrage Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Strategy](https://img.shields.io/badge/Strategy-Statistical%20Arbitrage-green?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Event--Driven-orange?style=for-the-badge)

An event-driven backtesting engine built from scratch in Python to model and evaluate **Statistical Arbitrage (Pairs Trading)** strategies on cointegrated equity pairs ($KO$ / $PEP$). 

The engine decouples market data streaming, signal calculation, order execution, and risk tracking to eliminate lookahead bias and closely mirror live quantitative trading infrastructure.

---

## 📐 Mathematical Framework

### 1. Asset Price Ratio & Rolling Spread
The strategy models the price relation between two cointegrated assets, Asset $A$ ($KO$) and Asset $B$ ($PEP$):

$$\text{Spread}_t = \frac{P_{A,t}}{P_{B,t}}$$

### 2. Rolling Z-Score Calculation
To detect mean-reversion opportunities, we compute a 30-day rolling $Z$-score of the spread:

$$Z_t = \frac{\text{Spread}_t - \mu_{\text{spread}, 30}}{\sigma_{\text{spread}, 30}}$$

* **Long Pair Signal ($Z_t \le -2.0$):** Spread is undervalued. Buy $KO$, Short $PEP$.
* **Short Pair Signal ($Z_t \ge +2.0$):** Spread is overvalued. Short $KO$, Buy $PEP$.
* **Mean Reversion Exit ($\vert{}Z_t\vert{} < 0.5$):** Spread has reverted to mean. Close both legs.

---

## 🏗️ System Architecture

The execution pipeline uses a central Event Queue loop:

```mermaid
graph TD
    A[HistoricDataHandler] -->|MarketEvent| Queue((Event Queue))
    Queue -->|MarketEvent| B[PairsStatArbStrategy]
    Queue -->|MarketEvent| C[Portfolio]
    B -->|SignalEvent| Queue
    Queue -->|SignalEvent| C
    C -->|OrderEvent| Queue
    Queue -->|OrderEvent| D[SimulatedExecutionHandler]
    D -->|FillEvent| Queue
    Queue -->|FillEvent| C