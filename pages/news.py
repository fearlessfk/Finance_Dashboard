import streamlit as st
from datetime import datetime
from config import (
    MAX_NEWS_DISPLAY, NEWS_COL_RATIO, THUMBNAIL_WIDTH
)
from logic_data import get_data

# ========== 页面基础设置 ==========
st.set_page_config(layout="wide", page_title="股票新闻 | Stock Dashboard")

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

st.title("📰 股票最新新闻")
st.markdown('---')

# ========== 读取全局共享的股票代码/周期 ==========
if 'ticker_symbol' not in st.session_state or 'ticker_period' not in st.session_state:
    st.warning("⚠️ 请先返回主页面选择股票代码！")
    st.stop()

ticker_symbol = st.session_state.ticker_symbol
ticker_period = st.session_state.ticker_period

# ========== 拉取新闻及基础行情数据 ==========
df, info, news = get_data(ticker_symbol, ticker_period)

# ========== 顶部股票信息概览 ==========
short_name = info.get("shortName", ticker_symbol)
sector = info.get("sector", "未知板块")
industry = info.get("industry", "未知行业")

top_col1, top_col2, top_col3 = st.columns([2, 1.2, 1.2])
with top_col1:
    st.subheader(f"{short_name}（{ticker_symbol}）新闻流")
    st.caption(f"{sector} · {industry}")
with top_col2:
    last_close = df["Close"].iloc[-1] if not df.empty else None
    st.metric("最新收盘价", f"{last_close:.2f}" if last_close else "暂无")
with top_col3:
    st.metric("新闻条数", f"{min(len(news), MAX_NEWS_DISPLAY)} / {len(news)}")

st.markdown("---")

# ========== 新闻解析与展示（原tab2逻辑完整迁移） ==========
st.subheader(f'关于 {ticker_symbol} 的最新新闻')


def parse_news_item(news_item):
    """解析单条新闻JSON，返回格式化后的字段"""
    content = news_item.get("content", {}) or {}  # 增强容错
    # 提取核心字段（带多层容错）
    news_link = content.get("canonicalUrl", {}).get("url", "#")
    title = content.get("title", "标题缺失")
    summary = content.get("summary", "摘要缺失")
    pub_date = content.get("pubDate", "时间未知")

    # 时间格式转换（容错）
    try:
        pub_time = datetime.fromisoformat(pub_date.replace(
            "Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")
    except:
        pub_time = pub_date

    # 提取缩略图（优先取170x128小图，容错）
    thumbnail_dict = content.get("thumbnail", {}) or {}
    resolutions = thumbnail_dict.get("resolutions", []) or []
    thumbnail_item = resolutions[1] if len(resolutions) >= 2 else {}
    thumbnail = thumbnail_item.get("url", "")

    return {
        "title": title,
        "link": news_link,
        "summary": summary,
        "publish_time": pub_time,
        "thumbnail": thumbnail
    }


# 展示新闻
if len(news) > 0:
    view_tab1, view_tab2 = st.tabs(["📰 新闻列表", "⏱ 时间轴视图"])

    with view_tab1:
        top5_news = news[:MAX_NEWS_DISPLAY]
        for idx, news_item in enumerate(top5_news, 1):
            parsed_news = parse_news_item(news_item)

            st.markdown(f"### {idx}. {parsed_news['title']}")
            col_thumb, col_content = st.columns(NEWS_COL_RATIO)
            with col_thumb:
                if parsed_news["thumbnail"]:
                    st.image(parsed_news["thumbnail"], width=THUMBNAIL_WIDTH)
                else:
                    st.write("🖼️ 无图")

            with col_content:
                st.caption(f"发布时间：{parsed_news['publish_time']}")
                st.write(f"**摘要**：{parsed_news['summary']}")
                st.markdown(f"[阅读全文]({parsed_news['link']})")

            st.divider()

    with view_tab2:
        # 简单时间轴：仅展示标题 + 时间
        for idx, news_item in enumerate(news[:MAX_NEWS_DISPLAY], 1):
            parsed_news = parse_news_item(news_item)
            st.markdown(
                f"- **{parsed_news['publish_time']}** ｜ [{parsed_news['title']}]({parsed_news['link']})"
            )
else:
    st.info("无新闻数据")

# ========== 返回主页面按钮（统一为卡片式导航） ==========
st.markdown('---')
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    st.page_link("main.py", label="🏠 回到主页面（行情 & 图表）")
with nav_col2:
    st.page_link("pages/fundamental.py", label="🏢 查看公司基本面")
