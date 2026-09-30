import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_performance_metrics(equity_df: pd.DataFrame) -> dict:
    returns = equity_df['equity'].pct_change().dropna()
    
    total_return = ((equity_df['equity'].iloc[-1] - equity_df['equity'].iloc[0]) / equity_df['equity'].iloc[0]) * 100
    
    # Calculate Sharpe Ratio with zero-std protection
    if len(returns) == 0 or returns.std() == 0:
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)

    # Max Drawdown
    rolling_max = equity_df['equity'].cummax()
    drawdown = (equity_df['equity'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100

    return {
        "Total Return (%)": total_return,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown (%)": max_drawdown
    }

def plot_equity_curve(equity_df: pd.DataFrame, filename: str = "equity_curve.png"):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    
    ax1.plot(equity_df.index, equity_df['equity'], label="Statistical Arbitrage Portfolio", color='#1f77b4', linewidth=1.5)
    ax1.set_title("Pairs Trading Strategy: Cumulative Performance (KO / PEP)")
    ax1.set_ylabel("Portfolio Value ($)")
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle='--', alpha=0.5)

    rolling_max = equity_df['equity'].cummax()
    drawdown = (equity_df['equity'] - rolling_max) / rolling_max * 100
    ax2.fill_between(equity_df.index, drawdown, 0, color='#e74c3c', alpha=0.4, label="Drawdown (%)")
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Date")
    ax2.legend(loc="lower left")
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()