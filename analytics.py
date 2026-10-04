import pandas as pd
import matplotlib.pyplot as plt

def plot_equity_curve(portfolio_or_df, output_filename="equity_curve.png"):
    """
    Plots and saves the portfolio equity curve and drawdown metrics.
    Accepts either a Portfolio instance or a pandas DataFrame.
    """
    # 1. Safely extract DataFrame
    if hasattr(portfolio_or_df, 'equity_curve'):
        raw_data = portfolio_or_df.equity_curve
        equity_df = pd.DataFrame(raw_data) if isinstance(raw_data, list) else raw_data
    elif isinstance(portfolio_or_df, pd.DataFrame):
        equity_df = portfolio_or_df
    else:
        equity_df = pd.DataFrame()

    if equity_df.empty or 'equity' not in equity_df.columns:
        print("Warning: Equity curve data is empty or missing 'equity' column. Unable to generate plot.")
        return

    df = equity_df.copy()

    # 2. Compute Drawdown Metrics
    df['peak'] = df['equity'].cummax()
    df['drawdown'] = (df['equity'] - df['peak']) / df['peak']

    # 3. Plot Performance
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    ax1.plot(df.index, df['equity'], label='Statistical Arbitrage Portfolio', color='#1f77b4', linewidth=1.5)
    ax1.set_title('Pairs Trading Strategy: Cumulative Performance (XOM / CVX)')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper left')

    ax2.fill_between(df.index, df['drawdown'], 0, color='red', alpha=0.3, label='Drawdown (%)')
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_xlabel('Step / Date')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='lower left')

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    plt.close()
    print(f"Successfully generated and saved updated chart to {output_filename}")