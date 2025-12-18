import streamlit as st
import yfinance as yf
import pandas as pd

from config import WATCHLIST, DEFAULT_PERIOD


@st.cache_data(ttl=1800)
def fetch_watchlist_data(symbols, period):
    """批量拉取自选股价格与简单技术指标（收盘价、涨跌幅、RSI）。"""
    data_rows = []
    for symbol in symbols:
        try:
            df = yf.download(symbol, period=period, progress=False)
            if df.empty or len(df) < 2:
                continue
            close = df["Close"].iloc[-1]
            prev_close = df["Close"].iloc[-2]
            delta = close - prev_close
            delta_pct = delta / prev_close * 100

            # 简单 RSI 计算（14期）
            price_change = df["Close"].diff().dropna()
            gain = price_change.where(price_change > 0, 0).rolling(14).mean()
            loss = (-price_change.where(price_change < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            latest_rsi = float(rsi.iloc[-1]) if not rsi.dropna().empty else None

            data_rows.append(
                {
                    "代码": symbol,
                    "最新价": round(close, 2),
                    "涨跌额": round(delta, 2),
                    "涨跌幅(%)": round(delta_pct, 2),
                    "RSI": round(latest_rsi, 1) if latest_rsi is not None else None,
                }
            )
        except Exception:
            continue

    if not data_rows:
        return pd.DataFrame()
    return pd.DataFrame(data_rows)


def show_watchlist():
    """展示自选股观察列表。"""
    st.subheader("📋 自选股观察列表")
    st.caption("快速浏览多只股票的最新价格、日内涨跌与RSI水平。")

    period = st.selectbox(
        "选择观察周期（用于计算RSI）",
        options=["3mo", "6mo", "1y"],
        index=1 if DEFAULT_PERIOD not in ["3mo", "6mo", "1y"] else ["3mo", "6mo", "1y"].index(DEFAULT_PERIOD),
        key="watchlist_period",
    )

    df_watch = fetch_watchlist_data(WATCHLIST, period)
    if df_watch.empty:
        st.info("当前自选股列表暂无可用数据，请检查 WATCHLIST 配置或网络连接。")
        return

    # 根据涨跌幅给出简单信号（显式处理单元格为 Series/非数值的情况）
    def _signal_from_change(x):
        # 某些情况下单元格可能是 Series，这里统一取最后一个标量
        if isinstance(x, pd.Series):
            if x.empty:
                return "HOLD"
            x = x.iloc[-1]
        try:
            v = float(x)
        except (TypeError, ValueError):
            return "HOLD"
        if v <= -2:
            return "BUY"
        elif v >= 2:
            return "SELL"
        return "HOLD"

    df_watch["信号"] = df_watch["涨跌幅(%)"].apply(_signal_from_change)

    st.dataframe(
        df_watch.set_index("代码"),
        use_container_width=True,
    )


