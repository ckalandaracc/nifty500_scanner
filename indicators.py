from typing import Optional
import pandas as pd


def compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI using Wilder's smoothing method.

    Args:
        prices: Series of closing prices indexed by date.
        period: lookback period (default 14).

    Returns:
        pd.Series of RSI values aligned to the input index.
    """
    delta = prices.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)

    # Wilder's smoothing (exponential moving average with alpha=1/period)
    roll_up = up.ewm(alpha=1 / period, adjust=False).mean()
    roll_down = down.ewm(alpha=1 / period, adjust=False).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_volume_ratio(volumes: pd.Series, window: int = 20) -> Optional[float]:
    """Compute volume ratio = latest_volume / SMA(volume, window).

    Returns None if insufficient data.
    """
    if len(volumes.dropna()) < window + 1:
        return None
    sma = volumes.rolling(window=window).mean()
    latest = volumes.iloc[-1]
    avg = sma.iloc[-1]
    if pd.isna(avg) or avg == 0:
        return None
    return float(latest / avg)
