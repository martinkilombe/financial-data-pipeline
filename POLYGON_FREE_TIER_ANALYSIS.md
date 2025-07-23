# Polygon.io Free Tier Analysis

## Free Plan ("Stocks Basic") Features

Based on research of Polygon.io's pricing and documentation:

### Included Features:
- **5 API Calls per Minute** rate limit
- **2 Years of Historical Data**
- **100% Market Coverage** for US stocks
- **End of Day Data**
- **Minute Aggregates** (historical)
- Reference Data
- Fundamentals Data
- Corporate Actions
- Technical Indicators

### Live/Real-time Data Availability:

**NO REAL-TIME DATA on Free Plan**

The free tier appears to provide:
- **End-of-day data** only for current market data
- **Historical minute bars** (with delay)
- **Last trade endpoint** (`/v2/last/trade/{ticker}`) - provides "latest available" trade but likely delayed

### Key Limitations:

1. **Data Delay**: Free tier likely has 15-20 minute delay (standard for free financial data)
2. **Rate Limit**: Only 5 API calls per minute
3. **No WebSocket/Streaming**: Real-time streaming requires paid plans
4. **Historical Focus**: Best suited for historical analysis, not live trading

### Available Endpoints on Free Tier:

1. **Aggregates (Bars)**: `/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}`
   - Historical minute, hour, day bars
   - Up to 2 years of data

2. **Previous Day**: `/v2/aggs/ticker/{ticker}/prev`
   - Yesterday's OHLC data

3. **Last Trade**: `/v2/last/trade/{ticker}`
   - Most recent trade (delayed)

4. **Last Quote**: `/v2/last/nbbo/{ticker}`
   - Most recent quote (delayed)

### Recommendation:

For live/real-time data, you would need:
- **Stocks Starter** ($29/month) - "Real-time data" mentioned
- **Stocks Developer** ($149/month) - Higher rate limits
- **WebSocket access** - Only on paid plans

The free plan is suitable for:
- Historical analysis
- End-of-day strategies
- Learning/testing the API
- Non-time-sensitive applications