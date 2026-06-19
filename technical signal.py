import yfinance as yf
import pandas as pd
import ta
import numpy as np


def calculate_fibonacci_levels(data, lookback_days=126):
    """
    Calculates Fibonacci Retracement levels based on the high and low
    of the last 'lookback_days' (approx 6 months).
    """
    try:
        # Find the high and low over the lookback period
        period_data = data.iloc[-lookback_days:]
        recent_high = period_data['High'].max()
        recent_low = period_data['Low'].min()

        price_range = recent_high - recent_low

        levels = {
            'level_0.0 (High)': recent_high,
            'level_0.236': recent_high - (price_range * 0.236),
            'level_0.382': recent_high - (price_range * 0.382),
            'level_0.5': recent_high - (price_range * 0.5),
            'level_0.618': recent_high - (price_range * 0.618),
            'level_1.0 (Low)': recent_low,
        }
        return levels
    except Exception as e:
        print(f"Error in Fibonacci calc: {e}")
        return {}


def get_technical_recommendation(ticker_symbol):
    """
    Fetches daily data and generates a Buy/Sell recommendation based
    on a basket of technical indicators.
    """
    print(f"\n--- Analyzing Technicals for: {ticker_symbol} ---")

    # 1. Fetch 1 year of daily data
    try:
        data = yf.download(ticker_symbol, period='1y', interval='1d', auto_adjust=True, progress=False)
        if data.empty:
            print(f"No data fetched for {ticker_symbol}. Is the ticker correct?")
            return
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Get the latest price and cast to float immediately
    # This prevents ambiguity errors in all future comparisons
    try:
        last_price = float(data['Close'].iloc[-1])
    except (IndexError, TypeError):
        print("Error getting last price. No data?")
        return

    # --- 2. Calculate All Indicators ---

    # Squeeze the data to ensure it's 1-dimensional for the 'ta' library
    # This is the fix for the ValueError: Data must be 1-dimensional
    close_series = data['Close'].squeeze()
    high_series = data['High'].squeeze()
    low_series = data['Low'].squeeze()

    # Add all indicators to the DataFrame
    try:
        # MA (50-day and 200-day)
        data['MA_50'] = ta.trend.sma_indicator(close_series, window=50)
        data['MA_200'] = ta.trend.sma_indicator(close_series, window=200)

        # EMA (20-day)
        data['EMA_20'] = ta.trend.ema_indicator(close_series, window=20)

        # Stochastic Oscillator (14, 3, 3)
        data['Stoch_K'] = ta.momentum.stoch(high_series, low_series, close_series, window=14, smooth_window=3)

        # MACD (12, 26, 9)
        macd = ta.trend.MACD(close_series, window_slow=26, window_fast=12, window_sign=9)
        data['MACD_line'] = macd.macd()
        data['MACD_signal'] = macd.macd_signal()

        # Bollinger Bands (20, 2)
        bollinger = ta.volatility.BollingerBands(close_series, window=20, window_dev=2)
        data['BB_High'] = bollinger.bollinger_hband()
        data['BB_Low'] = bollinger.bollinger_lband()

        # RSI (14)
        data['RSI'] = ta.momentum.rsi(close_series, window=14)

        # Fibonacci Levels
        fib_levels = calculate_fibonacci_levels(data)

    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return

    # --- 3. Get Current Values and Generate Score ---

    print(f"\nLast Price: {last_price:,.2f}\n")  # This is now safe, last_price is a float
    print("--- Indicator Analysis ---")

    score = 0
    analysis = []

    # Get the most recent indicator values
    try:
        # Cast all indicator values to float() to prevent comparison errors

        # MA Analysis (Trend)
        ma_50 = float(data['MA_50'].iloc[-1])
        ma_200 = float(data['MA_200'].iloc[-1])
        if ma_50 > ma_200:
            score += 1
            analysis.append(f"MA(50) > MA(200): BUY (Medium-term trend is up)")
        else:
            score -= 1
            analysis.append(f"MA(50) < MA(200): SELL (Medium-term trend is down)")

        # EMA Analysis (Short-term)
        ema_20 = float(data['EMA_20'].iloc[-1])
        if last_price > ema_20:
            score += 1
            analysis.append(f"Price > EMA(20): BUY (Short-term momentum is up)")
        else:
            score -= 1
            analysis.append(f"Price < EMA(20): SELL (Short-term momentum is down)")

        # Stochastic Analysis (Overbought/Oversold)
        stoch_k = float(data['Stoch_K'].iloc[-1])
        if stoch_k < 20:
            score += 1
            analysis.append(f"Stochastic < 20: BUY (Oversold)")
        elif stoch_k > 80:
            score -= 1
            analysis.append(f"Stochastic > 80: SELL (Overbought)")
        else:
            analysis.append(f"Stochastic = {stoch_k:.2f}: NEUTRAL")

        # MACD Analysis (Momentum)
        macd_line = float(data['MACD_line'].iloc[-1])
        macd_signal = float(data['MACD_signal'].iloc[-1])
        if macd_line > macd_signal:
            score += 1
            analysis.append(f"MACD > Signal: BUY (Momentum is bullish)")
        else:
            score -= 1
            analysis.append(f"MACD < Signal: SELL (Momentum is bearish)")

        # Bollinger Bands Analysis (Volatility/Reversion)
        bb_high = float(data['BB_High'].iloc[-1])
        bb_low = float(data['BB_Low'].iloc[-1])
        if last_price < bb_low:
            score += 1
            analysis.append(f"Price < Lower BB: BUY (Potentially oversold, mean reversion)")
        elif last_price > bb_high:
            score -= 1
            analysis.append(f"Price > Upper BB: SELL (Potentially overbought, mean reversion)")
        else:
            analysis.append(f"Price inside BB: NEUTRAL")

        # RSI Analysis (Overbought/Oversold)
        rsi = float(data['RSI'].iloc[-1])
        if rsi < 30:
            score += 1
            analysis.append(f"RSI < 30: BUY (Oversold)")
        elif rsi > 70:
            score -= 1
            analysis.append(f"RSI > 70: SELL (Overbought)")
        else:
            analysis.append(f"RSI = {rsi:.2f}: NEUTRAL")

        # Fibonacci Analysis (Support/Resistance)
        if fib_levels:
            # Check if price is near a support level (0.618 or 0.5)
            support_618 = float(fib_levels['level_0.618'])
            if abs(last_price - support_618) / last_price < 0.01:  # Within 1% of 0.618 level
                score += 1
                analysis.append(f"Price near Fib 0.618 support: BUY")
            else:
                analysis.append(f"Price not near Fib 0.618 support ({support_618:.2f})")

    except (IndexError, ValueError) as e:
        print(f"Not enough data to calculate all indicators (e.g., new listing). Error: {e}")
        return

    # --- 4. Final Recommendation ---
    print("\n--- Summary ---")
    for line in analysis:
        print(f"• {line}")

    print("\n--- FINAL RECOMMENDATION ---")
    if score >= 3:
        print(f"STRONG BUY (Score: {score})")
    elif score > 0:
        print(f"BUY (Score: {score})")
    elif score <= -3:
        print(f"STRONG SELL (Score: {score})")
    elif score < 0:
        print(f"SELL (Score: {score})")
    else:
        print(f"NEUTRAL (Score: {score})")

    print("\nDISCLAIMER: This is not financial advice. All analysis is based on")
    print("past performance and standard technical indicators. Do your own research.")


# --- Main execution ---
if __name__ == "__main__":

    # Get ticker input from user
    ticker_input = input("Enter stock ticker (e.g., RELIANCE, TCS, or ^NSEI for NIFTY 50): ").strip().upper()

    # Automatically append .NS if it's not an index (doesn't start with ^) and doesn't already have .NS
    if not ticker_input.startswith('^') and not ticker_input.endswith('.NS'):
        TICKER = ticker_input + '.NS'
        print(f"Assuming Indian stock, using: {TICKER}")
    else:
        TICKER = ticker_input

    get_technical_recommendation(TICKER)

