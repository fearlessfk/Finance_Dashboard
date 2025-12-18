# 1. 核心库导入
import streamlit as st
import pandas as pd

# 2. 本地配置&逻辑模块导入（充分利用config配置项）
from config import (
    PAGE_LAYOUT,  # 页面布局配置
    PAGE_TITLE,   # 页面标题配置
    CACHE_TTL     # 缓存时间（可用于扩展）
)
from logic_data import get_data, get_balance_sheet

# ========== 页面基础设置（使用config中的标准化配置） ==========
st.set_page_config(
    layout=PAGE_LAYOUT,  # 替代硬编码的"wide"
    page_title=f"公司基本面 | {PAGE_TITLE}"  # 统一标题格式
)

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Microsoft Yahei", sans-serif;
            background: radial-gradient(circle at top left, #e5f0ff 0, #f9fafb 40%, #ffffff 100%);
        }
        [data-testid="stAppViewContainer"] > .main {
            padding-top: 1.3rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
        h1 {
            font-size: 1.45rem;
            font-weight: 650;
            letter-spacing: 0.06em;
            color: #0f172a;
        }
        h2, h3 {
            letter-spacing: 0.04em;
        }
        p, span, li {
            font-size: 0.95rem;
            line-height: 1.6;
            color: #111827;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("🏢 公司基本面信息")
st.markdown('---')

# ========== 读取全局共享的股票代码 ==========
if 'ticker_symbol' not in st.session_state:
    st.warning("⚠️ 请先返回主页面选择股票代码！")
    st.stop()

ticker_symbol = st.session_state.ticker_symbol

# ========== 拉取基本面数据 ==========
_, info, _ = get_data(ticker_symbol, "")  # 周期不影响基本面，传空即可

# ========== 顶部公司概览卡片 ==========
short_name = info.get("shortName", ticker_symbol)
sector = info.get("sector", "未知板块")
industry = info.get("industry", "未知行业")
country = info.get("country", "未知国家/地区")
website = info.get("website", "")

top_col1, top_col2, top_col3 = st.columns([2, 1.2, 1.2])
with top_col1:
    st.subheader(f"{short_name}（{ticker_symbol}）")
    st.caption(f"{country} · {sector} · {industry}")
    if website:
        st.markdown(f"[官方网站]({website})")

with top_col2:
    st.metric(
        "最新价 (USD)",
        f"{info.get('currentPrice', 0):.2f}" if info.get("currentPrice") else "未知",
    )
with top_col3:
    market_cap = info.get("marketCap")
    mc_str = f"{market_cap/1e9:.2f} B" if market_cap else "未知"
    st.metric("市值 (Market Cap)", mc_str)

st.markdown("---")

# ========== 公司概况展示 ==========
st.subheader("公司概况")
# 1. 公司简介（强容错）
company_intro = info.get('longBusinessSummary', '暂无公司简介')
st.write(company_intro)

st.markdown("---")

# 2. 分栏展示财务指标和资产负债表
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.subheader("主要财务指标")
    # 构造财务指标字典（标准化格式）
    metrics = {
        "市盈率 (PE Ratio)": f"{info.get('trailingPE', '未知'):.2f}" if info.get('trailingPE') else "未知",
        "预期市盈率 (Forward PE)": f"{info.get('forwardPE', '未知'):.2f}" if info.get('forwardPE') else "未知",
        "市净率 (Price/Book)": f"{info.get('priceToBook', '未知'):.2f}" if info.get('priceToBook') else "未知",
        "市值 (Market Cap)": f"${info.get('marketCap', 0)/1e9:.2f}B" if info.get('marketCap') else "未知",
        "52周最高": f"${info.get('fiftyTwoWeekHigh', '未知'):.2f}" if info.get('fiftyTwoWeekHigh') else "未知",
        "52周最低": f"${info.get('fiftyTwoWeekLow', '未知'):.2f}" if info.get('fiftyTwoWeekLow') else "未知",
        "股息率 (Dividend Yield)": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "暂无股息",
    }
    # 转换为表格展示
    st.table(pd.DataFrame(metrics.items(), columns=['指标', '数值']))

with col_f2:
    st.subheader("资产负债表 (最新)")
    balance_sheet = get_balance_sheet(ticker_symbol)
    if not balance_sheet.empty:
        # 展示前10行，保留2位小数
        st.dataframe(
            balance_sheet.head(10).round(2),
            use_container_width=True
        )
    else:
        st.info("暂无资产负债表数据")

st.markdown("---")

# ========== 补充：公司关键信息速览 ==========
st.subheader("公司关键信息速览")
info_col1, info_col2, info_col3 = st.columns(3)
with info_col1:
    st.markdown("**员工人数**")
    employees = info.get("fullTimeEmployees")
    st.write(f"{employees:,}" if employees else "未知")
with info_col2:
    st.markdown("**成立年份**")
    st.write(info.get("yearFounded", "未知"))
with info_col3:
    st.markdown("**上市交易所**")
    st.write(info.get("exchange", "未知"))

# ========== 返回主页面按钮（统一为卡片式导航） ==========
st.markdown('---')
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    st.page_link("main.py", label="🏠 回到主页面（行情 & 图表）")
with nav_col2:
    st.page_link("pages/news.py", label="📰 查看相关新闻")
