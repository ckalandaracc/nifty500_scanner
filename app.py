"""Streamlit UI for Nifty 500 Scanner.

Run with:
    streamlit run app.py --server.port=8502 --server.address=0.0.0.0
"""
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from config import REFRESH_INTERVAL_MINUTES
from scanner import scan_market

st.set_page_config(
    page_title="Nifty 500 Scanner",
    layout="wide",
    page_icon="📈",
)

TITLE = "Nifty 500 Scanner — P/E < 20, Volume Spike > 2×, RSI(14) > 50"
DESCRIPTION = (
    "Scan Nifty 500 NSE symbols with trailing P/E < 20, volume spike > 2× 20-day average, "
    "and RSI(14) > 50. Data is refreshed every 10 minutes and may be delayed by yfinance."
)

DEFAULT_DISPLAY_ROWS = 20
MAX_DISPLAY_ROWS = 100


def initialize_state() -> None:
    if "scan_results" not in st.session_state:
        st.session_state.scan_results = pd.DataFrame()
    if "last_scan" not in st.session_state:
        st.session_state.last_scan = None
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = None
    if "force_refresh" not in st.session_state:
        st.session_state.force_refresh = False
    if "scan_error" not in st.session_state:
        st.session_state.scan_error = ""


def should_refresh() -> bool:
    if st.session_state.force_refresh or st.session_state.last_refresh is None:
        return True
    next_refresh = st.session_state.last_refresh + timedelta(minutes=REFRESH_INTERVAL_MINUTES)
    return datetime.utcnow() >= next_refresh


def trigger_auto_refresh(interval_seconds: int) -> None:
    components.html(
        f"<script>setTimeout(() => window.location.reload(), {interval_seconds * 1000});</script>",
        height=0,
        width=0,
    )


def run_scan(top_n: int) -> None:
    try:
        results = scan_market(top_n=MAX_DISPLAY_ROWS)
        st.session_state.scan_results = results
        st.session_state.last_scan = datetime.utcnow()
        st.session_state.last_refresh = datetime.utcnow()
        st.session_state.scan_error = ""
    except Exception as exc:
        st.session_state.scan_error = str(exc)
    finally:
        st.session_state.force_refresh = False


def format_timestamp(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S UTC") if value else "Never"


initialize_state()

st.title(TITLE)
st.markdown(DESCRIPTION)

col1, col2 = st.columns([1, 2])
with col1:
    display_count = st.slider(
        "Number of stocks to display",
        min_value=5,
        max_value=MAX_DISPLAY_ROWS,
        value=DEFAULT_DISPLAY_ROWS,
        help="Choose how many top scan results to show.",
    )
    if st.button("Run Scan / Refresh now"):
        st.session_state.force_refresh = True

with col2:
    st.markdown(f"**Last successful scan:** {format_timestamp(st.session_state.last_scan)}")
    st.markdown(f"**Next auto-refresh:** {format_timestamp(st.session_state.last_refresh + timedelta(minutes=REFRESH_INTERVAL_MINUTES)) if st.session_state.last_refresh else 'Pending first scan'}")

if should_refresh():
    with st.spinner("Running Nifty 500 scan..."):
        run_scan(display_count)

if st.session_state.scan_error:
    st.error(f"Scan error: {st.session_state.scan_error}")

if st.session_state.scan_results.empty:
    st.warning("No results available yet. Run a scan or wait for the automatic refresh.")
else:
    st.subheader("Top scan results")
    display_df = st.session_state.scan_results.head(display_count).copy()
    display_df["pe_ratio"] = display_df["pe_ratio"].map(lambda x: f"{x:.2f}" if x is not None else "N/A")
    display_df["last_price"] = display_df["last_price"].map(lambda x: f"{x:.2f}" if x is not None else "N/A")
    display_df["volume_ratio"] = display_df["volume_ratio"].map(lambda x: f"{x:.2f}" if x is not None else "N/A")
    display_df["rsi"] = display_df["rsi"].map(lambda x: f"{x:.2f}" if x is not None else "N/A")
    st.dataframe(display_df, use_container_width=True)

trigger_auto_refresh(REFRESH_INTERVAL_MINUTES * 60)
