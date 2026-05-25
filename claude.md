# Nifty 500 Scanner — Project Instructions

This file documents the project conventions, objectives, and coding guidelines for the Nifty 500 trading scanner.

Project goal
- Build a Streamlit app that scans Nifty 500 (NSE) tickers and finds stocks satisfying:
  - Trailing P/E (TTM) > 0 and < 20
  - Volume spike: today's volume / 20-day average volume > 2.0
  - RSI(14) on daily close > 50
- Rank matches by `volume_ratio` descending and display top N (default 20).

Assumptions (defaults)
- RSI(14) uses Wilder's smoothing on daily close prices.
- Volume ratio is defined as `today_volume / sma(volume, 20)`.
- yfinance tickers for NSE use `SYMBOL.NS` format.
- Local universe file: `data/nifty500.csv` with a `symbol` column (recommended).
- App port: 8502 (see `config.py`).
- Refresh: automatic every 10 minutes + manual refresh button.

Coding style and conventions
- Target Python 3.10+. Use virtual environments (`python -m venv .venv`).
- PEP8 formatting. Keep functions small and focused.
- Use type hints for public functions and return types.
- Docstrings: triple-quoted `"""` for modules, functions, and classes. Describe args, returns, and exceptions.
- Avoid global mutable state; use function inputs/returns and explicit session state in Streamlit.

Error handling and robustness
- Per-ticker failures must not crash the whole scan. Catch exceptions per ticker, log a concise warning, and continue.
- Skip tickers with missing or invalid required fields (e.g., P/E missing or zero). Log the skip.
- Respect yfinance rate limits by batching requests and avoiding duplicate requests during the same scan.

Performance considerations
- Fetch OHLCV history and fundamentals in batches where possible. Cache results for the duration of a single scan cycle.
- Minimize repeated calls to yfinance for the same ticker within one refresh.
- Use vectorized pandas operations for indicators where possible.

Testing and local runs
- Keep functions small so they can be unit-tested independently (e.g., `compute_rsi`, `compute_volume_ratio`).
- Provide a small sample `data/nifty500.csv` with a few tickers for quick local tests.

Data and limitations
- Data source: `yfinance` (Yahoo Finance). Data may be delayed for NSE tickers and not suitable for real-time trading.
- This tool is for research and screening only — not trading advice.

Files and roles
- `requirements.txt` — Python package dependencies.
- `config.py` — constants (refresh interval, paths, server port).
- `data_fetcher.py` — functions to load tickers and fetch OHLCV and fundamentals.
- `indicators.py` — RSI and volume ratio computations.
- `scanner.py` — orchestration: load, fetch, compute, filter, and rank.
- `app.py` — Streamlit UI.
- `data/nifty500.csv` — local universe file (recommendation).

Workflow notes
- After code changes, run the Streamlit app with:

```
streamlit run app.py --server.port=8502 --server.address=0.0.0.0
```

- The app will store the last successful scan timestamp in Streamlit session state and automatically re-run the scan when the timestamp is older than `REFRESH_INTERVAL_MINUTES`.

Contact and ownership
- Keep this document in the project root. Update if conventions change.
