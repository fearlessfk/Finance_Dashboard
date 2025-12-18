import streamlit as st
import yfinance as yf
import pandas as pd


@st.cache_data(ttl=1800)
def fetch_price_series(symbol: str, period: str):
    df = yf.download(symbol, period=period, progress=False)
    return df[["Close"]].dropna()


def rsi_signal_strategy(df: pd.DataFrame, low=30, high=70):
    """基于RSI的简单多空策略：RSI<low 持有多头，RSI>high 空仓。"""
    close = df["Close"]
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    df = df.copy()
    df["RSI"] = rsi
    df["Position"] = 0
    df.loc[df["RSI"] < low, "Position"] = 1
    df.loc[df["RSI"] > high, "Position"] = 0
    df["Position"] = df["Position"].ffill().fillna(0)
    return df


def rsi_macd_combo_strategy(df: pd.DataFrame, rsi_low=30, rsi_high=70):
    """RSI + MACD 联合策略：
    - 当 RSI < rsi_low 且 MACD > Signal 时持有多头
    - 当 RSI > rsi_high 或 MACD < Signal 时清仓
    """
    df = df.copy()
    close = df["Close"]

    # 计算 RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    df["RSI"] = rsi

    # 计算 MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    df["MACD"] = macd
    df["MACD_Signal"] = signal

    # 建仓/平仓规则
    df["Position"] = 0

    # 开仓：RSI 超卖 + MACD 在 Signal 之上
    buy_cond = (df["RSI"] < rsi_low) & (df["MACD"] > df["MACD_Signal"])
    # 平仓：RSI 超买 或 MACD 跌破 Signal
    sell_cond = (df["RSI"] > rsi_high) | (df["MACD"] < df["MACD_Signal"])

    df.loc[buy_cond, "Position"] = 1
    df.loc[sell_cond, "Position"] = 0

    df["Position"] = df["Position"].ffill().fillna(0)
    return df


def compute_backtest(df: pd.DataFrame):
    """计算买入持有 vs 策略净值曲线。"""
    df = df.copy()
    df["Return"] = df["Close"].pct_change()
    df["StrategyReturn"] = df["Return"] * df["Position"].shift(1).fillna(0)

    df["Equity_BuyHold"] = (1 + df["Return"]).cumprod()
    df["Equity_Strategy"] = (1 + df["StrategyReturn"]).cumprod()
    return df


def show_backtest():
    """展示策略回测结果（支持 RSI / RSI+MACD 联合策略）。"""
    st.subheader("📐 策略回测实验室")
    st.caption("对当前选择的股票进行简单规则策略回测，对比买入持有表现。")

    if "ticker_symbol" not in st.session_state:
        st.info("请先在主页面选择一只股票。")
        return

    symbol = st.session_state.ticker_symbol
    period = st.selectbox(
        "回测区间",
        options=["6mo", "1y", "2y", "5y"],
        index=1,
        key="backtest_period",
    )

    strategy_type = st.radio(
        "选择策略",
        options=["仅RSI信号", "RSI + MACD 联合信号"],
        horizontal=True,
        key="backtest_strategy_type",
    )

    df = fetch_price_series(symbol, period)
    if df.empty or len(df) < 30:
        st.warning("该区间数据不足，无法回测。")
        return

    low = st.slider("RSI 买入阈值（低于该值建仓）", 10, 40, 30, step=1)
    high = st.slider("RSI 卖出阈值（高于该值清仓）", 60, 90, 70, step=1)

    if strategy_type == "仅RSI信号":
        df_with_pos = rsi_signal_strategy(df, low=low, high=high)
    else:  # RSI + MACD 联合信号
        df_with_pos = rsi_macd_combo_strategy(df, rsi_low=low, rsi_high=high)
    df_bt = compute_backtest(df_with_pos)

    # 统计指标
    equity_bh = df_bt["Equity_BuyHold"]
    equity_st = df_bt["Equity_Strategy"]
    final_bh = equity_bh.iloc[-1] - 1
    final_st = equity_st.iloc[-1] - 1

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("买入持有最终收益率", f"{final_bh * 100:.2f}%")
    with col_m2:
        st.metric("策略最终收益率", f"{final_st * 100:.2f}%")

    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(
        go.Line(
            x=equity_bh.index,
            y=equity_bh,
            name="买入持有",
            line=dict(color="#1f77b4", width=2),
        )
    )
    fig.add_trace(
        go.Line(
            x=equity_st.index,
            y=equity_st,
            name="策略净值",
            line=dict(color="#22c55e", width=2),
        )
    )
    fig.update_layout(
        title=f"{symbol} - 策略 vs 买入持有 净值曲线",
        yaxis_title="净值 (初始=1)",
        xaxis_title="日期",
        template="plotly_white",
        hovermode="x unified",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)


