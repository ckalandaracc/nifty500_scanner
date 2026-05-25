from typing import List, Optional
import logging
from datetime import datetime

import pandas as pd

from config import NIFTY500_CSV_PATH, YF_HISTORY_DAYS
import data_fetcher as dfetcher
import indicators as ind

logger = logging.getLogger(__name__)


def scan_market(tickers: Optional[List[str]] = None, top_n: int = 20) -> pd.DataFrame:
    """Scan the market and return top matching tickers.

    Args:
        tickers: optional list of yfinance tickers. If None, load from CSV path in config.
        top_n: maximum number of rows to return.

    Returns:
        DataFrame with columns ['ticker','last_price','pe_ratio','volume_ratio','rsi','last_update']
    """
    if tickers is None:
        tickers = dfetcher.load_nifty500_tickers(NIFTY500_CSV_PATH)

    results = []

    for ticker in tickers:
        try:
            hist = dfetcher.fetch_history(ticker, YF_HISTORY_DAYS)
        except Exception as exc:
            logger.warning("Failed to fetch history for %s: %s", ticker, exc)
            continue

        if hist is None or hist.empty or len(hist) < 21:
            logger.debug("Insufficient historical data for %s", ticker)
            continue

        try:
            rsi_series = ind.compute_rsi(hist["Close"].astype(float))
            rsi_val = float(rsi_series.iloc[-1]) if not rsi_series.empty else None
        except Exception as exc:
            logger.debug("RSI compute failed for %s: %s", ticker, exc)
            rsi_val = None

        try:
            vol_ratio = ind.compute_volume_ratio(hist["Volume"].astype(float), window=20)
        except Exception as exc:
            logger.debug("Volume ratio failed for %s: %s", ticker, exc)
            vol_ratio = None

        # Fetch fundamentals
        try:
            info = dfetcher.fetch_info(ticker)
        except Exception as exc:
            logger.debug("Info fetch failed for %s: %s", ticker, exc)
            info = {}

        # Extract P/E and current price with fallbacks
        pe = None
        for key in ("trailingPE", "trailing_pe", "peRatio"):
            if key in info and info.get(key) is not None:
                try:
                    pe = float(info.get(key))
                    break
                except Exception:
                    pe = None

        # Determine last price — prefer market data, else last close
        last_price = None
        for key in ("regularMarketPrice", "currentPrice", "last_price", "previousClose"):
            if key in info and info.get(key) is not None:
                try:
                    last_price = float(info.get(key))
                    break
                except Exception:
                    last_price = None
        if last_price is None:
            try:
                last_price = float(hist["Close"].iloc[-1])
            except Exception:
                last_price = None

        # Apply filters
        try:
            if pe is None or pe <= 0 or pe >= 20:
                continue
            if vol_ratio is None or vol_ratio <= 2.0:
                continue
            if rsi_val is None or rsi_val <= 50:
                continue
        except Exception:
            continue

        last_update = None
        try:
            last_update = pd.Timestamp(hist.index[-1]).isoformat()
        except Exception:
            last_update = datetime.utcnow().isoformat()

        results.append({
            "ticker": ticker,
            "last_price": last_price,
            "pe_ratio": pe,
            "volume_ratio": vol_ratio,
            "rsi": rsi_val,
            "last_update": last_update,
        })

        # throttle briefly to be polite to yfinance
        dfetcher.safe_sleep(0.2)

    if not results:
        cols = ["ticker", "last_price", "pe_ratio", "volume_ratio", "rsi", "last_update"]
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(results)
    df = df.sort_values(by="volume_ratio", ascending=False)
    return df.head(top_n).reset_index(drop=True)
