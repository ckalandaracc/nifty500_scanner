from pathlib import Path

# Server configuration
SERVER_PORT: int = 8502
SERVER_ADDRESS: str = "0.0.0.0"

# Refresh interval (minutes)
REFRESH_INTERVAL_MINUTES: int = 10

# Data paths
ROOT = Path(__file__).parent
NIFTY500_CSV_PATH = ROOT / "data" / "nifty500.csv"

# yfinance settings
YF_HISTORY_DAYS: int = 90  # fetch last 90 calendar days (~60 trading days)
