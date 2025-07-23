# Real-Time Stock API Comparison (2025)

## Overview
Most "free real-time" stock APIs actually provide 15-20 minute delayed data. True real-time data typically requires paid subscriptions.

## Top Free/Freemium Stock APIs

### 1. **Yahoo Finance (via yfinance)**
- **Real-time**: Yes, for major S&P 500 stocks
- **Delay**: Variable (some stocks delayed)
- **Free Tier**: Unlimited (but rate limited)
- **Rate Limit**: ~200-300 requests/day before blocking
- **Pros**: Completely free, Python library available
- **Cons**: Unofficial API, can break, IP blocking risk

### 2. **Alpha Vantage**
- **Real-time**: No (15-20 min delay on free tier)
- **Free Tier**: 500 requests/day, 5/minute
- **Features**: Stock data, forex, crypto, technical indicators
- **Pros**: Official API, reliable, good documentation
- **Cons**: Delayed data on free tier

### 3. **Finnhub**
- **Real-time**: Limited real-time on free tier
- **Free Tier**: 60 requests/minute
- **Features**: Stock prices, company fundamentals, news, sentiment
- **Pros**: Good alternative data (insider trades, sentiment)
- **Cons**: Limited historical data on free tier

### 4. **Twelve Data**
- **Real-time**: No (delayed on free tier)
- **Free Tier**: 800 requests/day
- **Features**: Stocks, forex, crypto, technical indicators
- **Pros**: 100+ technical indicators, global coverage
- **Cons**: Delayed data, limited historical access

### 5. **Marketstack**
- **Real-time**: No (end-of-day only on free tier)
- **Free Tier**: 1,000 requests/month
- **Features**: 170,000+ tickers, 70+ exchanges
- **Pros**: Wide coverage, easy to use
- **Cons**: No intraday data on free tier

### 6. **IEX Cloud**
- **Real-time**: Yes for IEX exchange only
- **Free Tier**: 50,000 messages/month
- **Features**: US stocks, forex, crypto
- **Pros**: True real-time for IEX trades
- **Cons**: Limited to IEX exchange volume (~2-3% of market)

## Best Options for Near Real-Time Data

### For Python Users:
```python
# yfinance - Completely free, real-time for major stocks
import yfinance as yf
ticker = yf.Ticker("AAPL")
current_price = ticker.info['currentPrice']
```

### For Higher Volume:
- **Alpha Vantage**: 500 requests/day free
- **Finnhub**: 60 requests/minute free

### For True Real-Time:
- **Polygon.io Paid**: Starting at $29/month
- **Market Data**: $9/month for 10K requests/day
- **Alpaca**: Free with brokerage account

## Recommendations by Use Case

### Learning/Personal Projects:
- **yfinance** - Free, easy to use
- **Alpha Vantage** - Reliable with good free tier

### Building an App:
- **Finnhub** - Good rate limits, alternative data
- **IEX Cloud** - Real-time IEX data

### Trading/Time-Sensitive:
- Consider paid options:
  - **Polygon.io**: <20ms latency
  - **Alpaca**: Free with account
  - **Interactive Brokers API**: With account

## Important Notes

1. **"Real-time" usually means 15-20 min delay** on free tiers
2. **True real-time data costs money** due to exchange fees
3. **Yahoo Finance is unofficial** but widely used
4. **Rate limits are strictly enforced** - respect them
5. **Consider WebSocket APIs** for streaming (usually paid)

## Quick Decision Tree

```
Need true real-time data?
├─ Yes → Consider paid options (Polygon, Alpaca, IBKR)
└─ No → 
    ├─ Python user? → yfinance
    ├─ Need reliability? → Alpha Vantage
    ├─ Need high rate limits? → Finnhub
    └─ Need global coverage? → Twelve Data
```