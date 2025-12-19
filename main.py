import streamlit as st
from config import (
    PAGE_LAYOUT, PAGE_TITLE, DEFAULT_TICKER, PERIOD_OPTIONS,
    DEFAULT_PERIOD_INDEX, SIDEBAR_INFO, PRESET_STOCKS, DEFAULT_PERIOD
)

from logic_data import get_data
from stock_comparison import show_stock_comparison
from watchlist import show_watchlist
from backtest import show_backtest
from logic_calc import calc_price_metrics, calc_sma_50, calc_RSI, calc_MACD
from logic_plot import plot_sma50, plot_rsi, plot_macd


# ========== 全局页面基础设置 & UI 主题美化 ==========
st.set_page_config(layout=PAGE_LAYOUT, page_title=PAGE_TITLE)

st.markdown(
    """
    <style>
        /* 全局字体与浅色背景 */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Microsoft Yahei", sans-serif;
            background: radial-gradient(circle at top left, #e5f0ff 0, #f9fafb 40%, #ffffff 100%);
        }

        /* 主体内容区域宽度与内边距优化 */
        [data-testid="stAppViewContainer"] > .main {
            padding-top: 1.4rem;
            padding-left: 3.1rem;
            padding-right: 3.1rem;
        }

        /* 全局正文文字 */
        p, span, li {
            font-size: 0.95rem;
            line-height: 1.6;
            color: #111827;
        }

        /* 顶部标题样式 */
        h1 {
            font-size: 1.5rem;
            font-weight: 650;
            letter-spacing: 0.06em;
            color: #0f172a;
        }
        h2 {
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            color: #111827;
        }
        h3 {
            font-size: 1rem;
            font-weight: 550;
            letter-spacing: 0.04em;
            color: #111827;
        }

        /* 指标卡统一样式（浅色专业风） */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff, #f3f4ff);
            border-radius: 0.85rem;
            padding: 0.9rem 1.1rem;
            box-shadow: 0 10px 30px rgba(15,23,42,0.08);
            border: 1px solid #e5e7eb;
        }
        div[data-testid="stMetric"] label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #6b7280 !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.35rem;
            font-weight: 720;
            color: #111827 !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-size: 0.9rem;
        }

        /* 侧边栏样式（浅色卡片风） */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f3f4ff 0%, #ffffff 60%, #f9fafb 100%);
            border-right: 1px solid #e5e7eb;
        }
        [data-testid="stSidebar"] * {
            font-size: 0.9rem;
        }

        /* 侧边栏：股票选择区域封装成独立卡片模块 */
        .sidebar-stock-card {
            padding: 1rem 0.9rem 1.1rem 0.9rem;
            margin-top: 0.7rem;
            margin-bottom: 1.1rem;
            border-radius: 1rem;
            border: 1px solid #e5e7eb;
            background: linear-gradient(135deg, #ffffff 0%, #f9fafb 55%, #eef2ff 100%);
            box-shadow: 0 12px 28px rgba(15,23,42,0.05);
        }
        .sidebar-stock-card h3 {
            font-size: 0.95rem;
            margin-bottom: 0.65rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #4b5563;
        }

        /* 侧边栏输入区域美化：选择框 + 文本框 */
        [data-testid="stSidebar"] [data-baseweb="select"],
        [data-testid="stSidebar"] input[type="text"] {
            background-color: #ffffff;
            border-radius: 0.6rem;
            border: 1px solid #d1d5db;
            box-shadow: 0 4px 10px rgba(15,23,42,0.04);
        }

        /* Tabs 标签样式 */
        button[data-baseweb="tab"] {
            font-size: 0.9rem;
            font-weight: 500;
        }

        /* 指标标题容器 */
        .indicator-title {
            margin-top: 0.9rem;
            margin-bottom: 0.6rem;
        }

        /* 分隔线间距优化 */
        hr {
            margin: 0.9rem 0 1.3rem 0;
            border-color: rgba(209,213,219,0.9);
        }

        /* 顶部「快速导航」中的页面跳转按钮卡片化 */
        a[data-testid="stPageLink"] {
            display: block;
            padding: 0.8rem 1.05rem;
            border-radius: 0.8rem;
            border: 1px solid #e5e7eb;
            background: linear-gradient(135deg, #ffffff, #f9fafb);
            box-shadow: 0 6px 18px rgba(15,23,42,0.05);
            text-decoration: none;
            color: #111827 !important;
        }
        a[data-testid="stPageLink"]:hover {
            border-color: #2563eb;
            box-shadow: 0 10px 24px rgba(37,99,235,0.15);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if 'current_indicator' not in st.session_state:
    st.session_state.current_indicator = "SMA50"

# 初始化股票代码/周期（用配置文件的默认值，更规范）
if 'ticker_symbol' not in st.session_state:
    st.session_state.ticker_symbol = DEFAULT_TICKER  # 首次加载用默认值
if 'ticker_period' not in st.session_state:
    st.session_state.ticker_period = DEFAULT_PERIOD


# ========== 2.一体化股票选择组件==========
def integrated_stock_selector(label, preset_options, default_code, key_prefix):
    """
    修复：下拉选择后强制同步状态+触发重渲染
    """
    st.sidebar.markdown(f"### {label}")
    preset_codes = [opt.split(" - ")[0].strip().upper()
                    for opt in preset_options]
    default_idx = preset_codes.index(
        default_code) + 1 if default_code in preset_codes else 0

    # 关键1：给下拉框添加on_change回调，强制同步状态
    def on_select_change():
        """下拉选择变化时的回调函数"""
        selected = st.session_state[f"{key_prefix}_select"]
        if selected != "📝 手动输入股票代码":
            # 提取选中的股票代码
            new_code = selected.split(" - ")[0].strip().upper()
            # 强制更新全局状态
            st.session_state.ticker_symbol = new_code
            # 触发页面重渲染
            st.rerun()

    # 下拉选择框添加on_change回调
    selected_preset = st.sidebar.selectbox(
        "快速选择",
        options=["📝 手动输入股票代码"] + preset_options,
        index=default_idx,
        key=f"{key_prefix}_select",
        label_visibility="collapsed",
        on_change=on_select_change  # 关键：选择变化时触发回调
    )

    # 输入框：优先使用全局状态的值（确保和下拉选择同步）
    if selected_preset == "📝 手动输入股票代码":
        # 手动输入模式：绑定全局状态
        ticker_input = st.sidebar.text_input(
            "请输入股票代码（如AAPL/MSFT）",
            value=st.session_state.ticker_symbol,  # 关键：用全局状态值
            key=f"{key_prefix}_input"
        ).strip().upper()
        # 手动输入变化时更新全局状态
        if ticker_input != st.session_state.ticker_symbol:
            st.session_state.ticker_symbol = ticker_input
            st.rerun()
    else:
        # 下拉选择模式：显示全局状态的值（禁用编辑）
        ticker_input = st.sidebar.text_input(
            "当前选择的股票代码",
            value=st.session_state.ticker_symbol,  # 关键：用全局状态值
            key=f"{key_prefix}_input",
            disabled=True
        )

    return st.session_state.ticker_symbol  # 直接返回全局状态值


tab1, tab2, tab3, tab4 = st.tabs(["📈 个股分析", "📊 收益率对比", "📋 自选股", "📐 策略回测"])

with tab1:
    # ========== 3. 页面顶部导航 ==========
    st.subheader("📌 快速导航")
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/news.py", label="查看最新新闻", icon="📰")
    with col2:
        st.page_link("pages/fundamental.py", label="查看公司基本面", icon="🏢")
    st.markdown("---")

    # ========== 4. 侧边栏：封装为「股票配置」独立模块 ==========
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-stock-card">
                <h3>MARKET CONFIG</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # 在卡片内部渲染组件
        with st.container():
            st.markdown("#### 🔍 股票搜索", help="在此选择你想分析的标的与时间范围")

            # 调用一体化选择器（替换原有文本输入框）
            ticker_symbol = integrated_stock_selector(
                label="选择/输入股票",
                preset_options=PRESET_STOCKS,
                default_code=DEFAULT_TICKER,
                key_prefix="main_stock"
            )

            # 原有周期选择逻辑（完全保留）
            ticker_period = st.selectbox(
                '请选择时间周期', PERIOD_OPTIONS, index=DEFAULT_PERIOD_INDEX)

            st.info(SIDEBAR_INFO)


    st.session_state.ticker_symbol = ticker_symbol  # 覆盖旧值
    st.session_state.ticker_period = ticker_period

    # ========== 全局状态存储（跨页面共享股票代码/周期） ==========
    if ticker_symbol != st.session_state.ticker_symbol:
        st.session_state.ticker_symbol = ticker_symbol
    if ticker_period != st.session_state.ticker_period:
        st.session_state.ticker_period = ticker_period


    df, info, news = get_data(st.session_state.ticker_symbol,st.session_state.ticker_period)

    # 初始化信号变量（防止未定义错误）
    signal_icon = "❓"
    status = "无数据"
    signal_reason = "无法获取股票数据"

    # 先统一计算技术指标，供上方指标卡与下方图表复用
    if not df.empty:
        df = calc_sma_50(df)
        df = calc_RSI(df)
        df = calc_MACD(df)

        # ========== 新增：调用信号判断函数（此时df有所有指标数据） ==========
        signal_icon, status, signal_reason = get_investment_signal(df)

    # ========== 顶部指标卡区域（类似彭博终端风格） ==========
    st.title(f"{info.get('shortName', ticker_symbol)} ({ticker_symbol}) 核心行情")
    current_price, delta, delta_percent = calc_price_metrics(df)

    if (current_price is not None) and (not df.empty):
        # 计算 RSI 当前值
        latest_rsi = df["RSI"].iloc[-1] if "RSI" in df.columns else None
        # 计算 MACD 最新信号（金叉 / 死叉 / 无明显信号）
        latest_macd_cross = df["MACD_Crossover"].iloc[-1] if "MACD_Crossover" in df.columns else 0
        if latest_macd_cross == 1:
            macd_signal_text = "金叉（买入信号）"
        elif latest_macd_cross == -1:
            macd_signal_text = "死叉（卖出信号）"
        else:
            macd_signal_text = "无明显信号"

        # 使用 st.columns 做成一行指标卡
        col_price, col_rsi, col_macd = st.columns(3)
        with col_price:
            # 使用 delta 显示日内涨跌箭头（正为绿色向上，负为红色向下）
            delta_str = f"{delta:+.2f} ({delta_percent:+.2f}%)"
            st.metric(
                label="当前价格（Close）",
                value=f"{current_price:.2f}",
                delta=delta_str,
                delta_color="normal"
            )
        with col_rsi:
            rsi_value_display = f"{latest_rsi:.2f}" if latest_rsi is not None else "N/A"
            st.metric(
                label="RSI（相对强弱指标）",
                value=rsi_value_display
            )
        with col_macd:
            st.metric(
                label="MACD 信号",
                value=macd_signal_text
            )



    # ========== 仅保留走势图（原tab1） ==========

    indicators = ["SMA50", "RSI", "MACD"]
    current_idx = indicators.index(st.session_state.current_indicator)

    # 指标标题+切换按钮
    st.markdown('<div class="indicator-title">', unsafe_allow_html=True)
    col_prev, col_title, col_next = st.columns([0.1, 0.8, 0.1])

    with col_prev:
        if st.button("⬅️", key="prev_indicator"):
            # 切换到上一个指标（循环）
            new_idx = (current_idx - 1) % len(indicators)
            st.session_state.current_indicator = indicators[new_idx]
        
    with col_title:
        st.subheader(f"📈 股价走势与技术指标 - {st.session_state.current_indicator}")

    with col_next:
        if st.button("➡️", key="next_indicator"):
            # 切换到下一个指标（循环）
            new_idx = (current_idx + 1) % len(indicators)
            st.session_state.current_indicator = indicators[new_idx]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== 计算对应指标并绘图 ==========
    if not df.empty:
        # 根据当前指标计算对应数据
        current_ind = st.session_state.current_indicator
        if current_ind == "SMA50":
            df = calc_sma_50(df)
        elif current_ind == "RSI":
            df = calc_RSI(df)
        elif current_ind == "MACD":
            df = calc_MACD(df)
        
        # 绘制对应指标图表
        if current_ind == "SMA50":
            fig = plot_sma50(df)
        elif current_ind == "RSI":
            fig = plot_rsi(df)
        elif current_ind == "MACD":
            fig = plot_macd(df)
        st.plotly_chart(fig, use_container_width=True)


    else:
        st.info("📊 暂无K线数据，请检查股票代码或时间周期")

    st.markdown("### 🚨 AI 投资信号")  # 醒目标题
    st.metric(
        label=f"{signal_icon} Current Signal",
        value=status,
        delta=f"判断依据：{signal_reason}",
        delta_color="inverse"  # 让原因更突出
    )
with tab2:
    show_stock_comparison()

with tab3:
    show_watchlist()

with tab4:
    show_backtest()