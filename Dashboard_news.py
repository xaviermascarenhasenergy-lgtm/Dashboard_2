import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Company Financial Dashboard", layout="wide")

st.title("📊 Company Financial Dashboard")

# --- Company selection ---
ticker_input = st.text_input("Enter a company ticker (e.g., AAPL, MSFT):", "AAPL").upper()

# Fetch stock data
@st.cache_data(ttl=3600)
def get_stock_data(ticker, period="20y", interval="1mo"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        hist.reset_index(inplace=True)
        return hist
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()

stock_df = get_stock_data(ticker_input)

if stock_df.empty:
    st.warning("No stock data available for this company.")
else:
    st.subheader(f"Stock Price of {ticker_input}")
    fig_stock = px.line(stock_df, x="Date", y="Close", title=f"{ticker_input} Stock Price")
    fig_stock.update_layout(yaxis_title="Price (USD)")
    st.plotly_chart(fig_stock, use_container_width=True)

# Fetch financials
@st.cache_data(ttl=3600)
def get_financials(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Financial metrics
        fin = stock.financials.T
        # Include Income Statement metrics
        income = stock.quarterly_financials.T
        return fin, income
    except Exception as e:
        st.error(f"Error fetching financials: {e}")
        return pd.DataFrame(), pd.DataFrame()

financials, quarterly_income = get_financials(ticker_input)

if not quarterly_income.empty:
    st.subheader(f"Quarterly Financials for {ticker_input}")
    cols_to_plot = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
    cols_existing = [col for col in cols_to_plot if col in quarterly_income.columns]
    if cols_existing:
        fig_fin = go.Figure()
        for col in cols_existing:
            fig_fin.add_trace(go.Bar(
                x=quarterly_income.index,
                y=quarterly_income[col],
                name=col
            ))
        fig_fin.update_layout(
            barmode="group",
            yaxis_title="USD",
            xaxis_title="Date"
        )
        st.plotly_chart(fig_fin, use_container_width=True)
    else:
        st.warning("No quarterly financial data available for the selected company.")

# --- Bloomberg news link ---
st.subheader(f"Latest Bloomberg News for {ticker_input}")
bloomberg_search_url = f"https://www.bloomberg.com/search?query={ticker_input}"
st.markdown(f"[Click here to view Bloomberg news for {ticker_input}]({bloomberg_search_url})", unsafe_allow_html=True)