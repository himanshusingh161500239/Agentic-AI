import yfinance as yf
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from database import write_market, read_market
from functools import lru_cache

load_dotenv(override=True)


def is_market_open() -> bool:
    """Check if NSE market is currently open (approximation via India time)."""
    # NSE market hours: 9:15 AM – 3:30 PM IST
    now = datetime.now().astimezone(timezone.utc)
    # Convert UTC to IST (+5:30)
    ist_now = now.astimezone()
    return ist_now.hour >= 9 and ist_now.hour < 15 and (
        ist_now.hour != 15 or ist_now.minute <= 30
    )


def get_all_share_prices_yf_eod(symbols: list[str]) -> dict[str, float]:
    """Get end-of-day closing prices for a list of NSE symbols via yfinance."""
    results = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(period="1d")
            if not hist.empty:
                results[symbol] = float(hist["Close"].iloc[-1])
            else:
                print(f"[YF] No history returned for {symbol}")
                results[symbol] = 0.0
        except Exception as e:
            print(f"[YF ERROR] {symbol}: {e}")
            results[symbol] = 0.0
    return results


@lru_cache(maxsize=2)
def get_market_for_prior_date(today: str, symbols: tuple[str, ...]):
    """Return cached market data for a date; fetch & store if missing."""
    market_data = read_market(today)
    if not market_data:
        market_data = get_all_share_prices_yf_eod(list(symbols))
        write_market(today, market_data)
    return market_data


def get_share_price_yf_eod(symbol: str) -> float:
    """Fetch last closing price (EOD) for a symbol."""
    today = datetime.now().date().strftime("%Y-%m-%d")
    market_data = get_market_for_prior_date(today, (symbol,))  
    return market_data.get(symbol, 0.0)


def get_share_price_yf_realtime(symbol: str) -> float:
    """Fetch near real-time price (delayed ~15 mins on NSE)."""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        price = ticker.info.get("regularMarketPrice")
        if price is not None:
            return float(price)
        # fallback: previous close
        return get_share_price_yf_eod(symbol)
    except Exception as e:
        print(f"[REALTIME ERROR] {symbol}: {e}")
        return get_share_price_yf_eod(symbol)


def get_share_price(symbol: str, realtime: bool = False) -> float:
    """Main entry point — NSE share price (EOD or realtime)."""
    print(f"[MARKET] get_share_price called with symbol={symbol}, realtime={realtime}")
    try:
        if realtime:
            return get_share_price_yf_realtime(symbol)
        else:
            return get_share_price_yf_eod(symbol)
    except Exception as e:
        print(f"[MARKET ERROR] Failed to fetch {symbol}: {e}")
        return 0.0 