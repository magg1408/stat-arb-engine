import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def calculate_performance_metrics(equity_df: pd.DataFrame, risk_free_rate=0.02):
    """
    Calculates Sharpe Ratio, Max Drawdown, and Total Return from equity history.
    """
    equity_df['returns'] = equity_df['equity'].pct_change().dropna()
    
    # 1. Total Return
    total_return = (equity_df['equity'].iloc[-1] - equity_df['equity'].iloc[0]) / equity_df['equity'].iloc[0]
    
    # 2. Annualized Sharpe Ratio (assuming 252 trading days)
    daily_rf = risk_free_rate / 252.0
    excess_returns = equity_df['returns'] - daily_rf
    sharpe_ratio = np.sqrt(252) * (excess_returns.mean() / excess_returns.std()) if excess_returns.std() != 0 else 0.0

    # 3. Maximum Drawdown Calculation
    equity_df['cum_max'] = equity_df['equity'].cummax()
    equity_df['drawdown'] = (equity_df['equity'] - equity_df['cum_max']) / equity_df['cum_max']
    max_drawdown = equity_df['drawdown'].min()

    return {
        "Total Return (%)": total_return * 100,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown (%)": max_drawdown * 100
    }

def plot_equity_curve(equity_df: pd.DataFrame, output_file="equity_curve.png"):
    """Saves formatted equity curve visualization to disk."""
    df = equity_df.copy()
    df.index = pd.to_datetime(df.index)  # Convert string timestamps to datetime

    plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # Equity Curve
    ax1.plot(df.index, df['equity'], label="Statistical Arbitrage Portfolio", color='#1f77b4', linewidth=1.5)
    ax1.set_title("Pairs Trading Strategy: Cumulative Performance (KO / PEP)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Portfolio Value ($)")
    ax1.legend(loc="upper left")

    # Drawdown Chart
    df['cum_max'] = df['equity'].cummax()
    drawdown = (df['equity'] - df['cum_max']) / df['cum_max'] * 100
    ax2.fill_between(df.index, drawdown, 0, color='red', alpha=0.3, label="Drawdown (%)")
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Date")
    ax2.legend(loc="lower left")

    # Format X-Axis Dates cleanly
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"\n[Analytics] Formatted equity curve saved as '{output_file}'")