from typing import List, Dict, Any
import time
from pathlib import Path
import logging

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def load_nifty500_tickers(path: str | Path) -> List[str]:
    """Load Nifty 500 tickers from a CSV file.

    Args:
        path: Path to CSV file with a `symbol` column (expects `SYMBOL.NS` format).

    Returns:
        List of ticker strings.
    """
    df = pd.read_csv(path)
    if "symbol" not in df.columns:
        raise ValueError("CSV must contain a 'symbol' column")
    return df["symbol"].dropna().astype(str).tolist()


def fetch_history(ticker: str, period_days: int) -> pd.DataFrame:
    """Fetch historical daily OHLCV for `ticker`.

    Args:
        ticker: yfinance ticker like 'RELIANCE.NS'.
        period_days: number of calendar days to fetch.

    Returns:
        DataFrame with DatetimeIndex and columns ['Open','High','Low','Close','Adj Close','Volume'].

    Notes:
        This function raises exceptions on failure; callers should catch per-ticker.
    """
    yf_t = yf.Ticker(ticker)
    hist = yf_t.history(period=f"{period_days}d", interval="1d", auto_adjust=False)
    return hist


def fetch_info(ticker: str) -> Dict[str, Any]:
    """Fetch fundamental info (e.g., trailingPE) and current price.

    Returns a dict merging `info` and `fast_info` where available.
    """
    yf_t = yf.Ticker(ticker)
    info = {}
    try:
        info = yf_t.info or {}
    except Exception as exc:  # yfinance can raise on bad tickers
        logger.debug("yfinance .info failed for %s: %s", ticker, exc)

    fast = {}
    try:
        fast = getattr(yf_t, "fast_info", {}) or {}
    except Exception:
        fast = {}

    combined = {**info, **fast}
    return combined


def safe_sleep(delay_seconds: float = 0.3) -> None:
    """Small helper to throttle requests between yfinance calls.

    Keep this conservative; callers may choose to skip sleeping when doing batch downloads.
    """
    time.sleep(delay_seconds)
