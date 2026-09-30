import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

def calculate_half_life(spread: pd.Series) -> float:
    """Estimates the half-life of mean reversion using an Ornstein-Uhlenbeck process."""
    spread_lag = spread.shift(1).dropna()
    spread_diff = spread.diff().dropna()
    
    # Align indices
    spread_lag = spread_lag.loc[spread_diff.index]
    
    # Linear regression: delta(spread) = gamma * spread_lag + const
    X = sm.add_constant(spread_lag)
    model = sm.OLS(spread_diff, X).fit()
    gamma = model.params.iloc[1]
    
    if gamma >= 0:
        return np.inf  # Non-mean-reverting process
        
    half_life = -np.log(2) / gamma
    return half_life

def screen_pairs(tickers, start_date="2023-01-01", end_date="2024-01-01", max_p_value=0.05):
    """
    Screens a universe of stock tickers for stationarity and cointegration.
    Returns ranked pairs based on ADF p-values and mean-reversion half-life.
    """
    print(f"Fetching market data for universe: {tickers}...")
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    data = data.dropna()
    
    results = []
    n = len(tickers)
    
    print("\n--- Running Cointegration Screening (Engle-Granger) ---")
    for i in range(n):
        for j in range(i + 1, n):
            stock_a = tickers[i]
            stock_b = tickers[j]
            
            price_a = data[stock_a]
            price_b = data[stock_b]
            
            # Step 1: Linear Regression Y = beta * X + alpha
            X = sm.add_constant(price_b)
            model = sm.OLS(price_a, X).fit()
            beta = model.params.iloc[1]
            
            # Step 2: Spread Residual Series
            spread = price_a - (beta * price_b)
            
            # Step 3: ADF Test for Stationarity
            adf_res = adfuller(spread)
            p_value = adf_res[1]
            
            if p_value <= max_p_value:
                half_life = calculate_half_life(spread)
                results.append({
                    'Pair': f"{stock_a} / {stock_b}",
                    'Beta': round(beta, 4),
                    'ADF p-value': round(p_value, 4),
                    'Half-Life (Days)': round(half_life, 2)
                })
                
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by='ADF p-value').reset_index(drop=True)
    return df_results

if __name__ == "__main__":
    # Test Screen across liquid large-caps
    universe = ["KO", "PEP", "XOM", "CVX", "JPM", "BAC", "MSFT", "AAPL"]
    pairs_df = screen_pairs(universe)
    print("\nCointegrated Pairs Summary:")
    print(pairs_df.to_string())