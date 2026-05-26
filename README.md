# Nifty 500 Scanner

A Streamlit-based screening tool for Nifty 500 NSE symbols. The app filters stocks by:
- Trailing P/E (TTM) between 0 and 20
- Volume spike > 2× the 20-day average volume
- RSI(14) above 50

It ranks matches by volume ratio and updates automatically every 10 minutes, with a manual refresh button.

## Requirements
- Python 3.10+
- `pip` available in the chosen Python environment

## Setup
1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```
for MAC
```
python3 -m venv .venv

source .venv/bin/activate

```
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Verify `data/nifty500.csv` exists and contains a `symbol` column with NSE tickers like `RELIANCE.NS`.

## Run

```bash
streamlit run app.py --server.port=8502 --server.address=0.0.0.0
```

Then open:

```text
http://localhost:8502
```

## Notes
- Data is sourced from Yahoo Finance via `yfinance`. NSE data may be delayed and incomplete.
- This tool is for research and screening only, not trading advice.
- The UI refreshes automatically every 10 minutes and also supports a manual refresh.

## Project files
- `config.py`: refresh interval and data path settings
- `data_fetcher.py`: loads tickers and fetches OHLCV/fundamentals
- `indicators.py`: computes RSI and volume spike metrics
- `scanner.py`: applies the filter rules and ranks results
- `app.py`: Streamlit UI and auto-refresh logic
