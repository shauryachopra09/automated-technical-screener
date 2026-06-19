# Automated Technical Screener

A Python tool that analyzes any stock against **7+ technical indicators simultaneously** and produces a single, clear recommendation — Strong Buy, Buy, Neutral, Sell, or Strong Sell — based on a weighted composite score.

---

## What This Does

Most traders check indicators one at a time — RSI here, MACD there, manually trying to piece together a view. This tool automates that entire process: it pulls a year of price data, calculates every major indicator at once, and combines them into a single composite score so you get a clear answer instead of seven separate, sometimes conflicting signals.

---

## Indicators Used

| Indicator | What It Measures |
|-----------|------------------|
| **Moving Averages (50/200-day)** | Medium-term trend direction (Golden Cross / Death Cross logic) |
| **EMA (20-day)** | Short-term momentum |
| **Stochastic Oscillator** | Overbought / oversold conditions |
| **MACD** | Trend momentum and potential reversals |
| **Bollinger Bands** | Volatility and mean-reversion signals |
| **RSI (14-day)** | Overbought / oversold strength |
| **Fibonacci Retracement** | Key support/resistance levels from the 6-month high/low range |

Each indicator contributes **+1** (bullish), **-1** (bearish), or **0** (neutral) to a composite score, which then maps to a final recommendation.

---

## How to Run

**1. Install dependencies**
```bash
pip install yfinance pandas numpy ta
```

**2. Run the script**
```bash
python technical_signal.py
```

**3. Follow the prompt**
```
Enter stock ticker (e.g., RELIANCE, TCS, or ^NSEI for NIFTY 50): INFY
```
The script automatically appends `.NS` for Indian stocks.

---

## Example Output

```
--- Analyzing Technicals for: INFY.NS ---

Last Price: 1,847.50

--- Indicator Analysis ---
• MA(50) > MA(200): BUY (Medium-term trend is up)
• Price > EMA(20): BUY (Short-term momentum is up)
• Stochastic = 45.30: NEUTRAL
• MACD > Signal: BUY (Momentum is bullish)
• Price inside BB: NEUTRAL
• RSI = 58.20: NEUTRAL
• Price not near Fib 0.618 support (1,720.40)

--- FINAL RECOMMENDATION ---
BUY (Score: 3)

DISCLAIMER: This is not financial advice. All analysis is based on
past performance and standard technical indicators. Do your own research.
```

---

## Scoring Logic

```
Score >= 3   →  STRONG BUY
Score > 0    →  BUY
Score = 0    →  NEUTRAL
Score <= -3  →  STRONG SELL
Score < 0    →  SELL
```

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| `yfinance` | 1-year daily OHLCV data |
| `ta` | Pre-built technical indicator calculations (MA, MACD, RSI, Bollinger, Stochastic) |
| `pandas` | Data handling and Series operations |
| `numpy` | Numerical comparisons |

---

## Key Design Decisions

**Why a composite score instead of a single indicator?** Single indicators frequently give false signals in isolation — RSI might say "oversold" while the trend is still firmly down. Combining 7 independent signals reduces the chance of acting on noise from any one indicator.

**Why Fibonacci levels specifically at 0.618?** The 61.8% retracement level is widely considered the strongest support/resistance level in Fibonacci analysis, making it the most reliable single level to test proximity against.

**Why squeeze the data before passing to `ta`?** The `ta` library expects strictly 1-dimensional Series. Multi-index columns from yfinance can cause dimensional mismatches, so each column is explicitly squeezed before indicator calculation.

---

## Limitations

- Equal-weighted scoring treats all 7 indicators as equally important, which may not reflect their actual predictive power
- No backtesting of the composite score's historical accuracy is included in this script (see the separate backtesting framework project for that methodology)
- Technical indicators work best in trending or range-bound markets and can give false signals during major news-driven moves

---

*This is not financial advice. Built for educational and research purposes.*
