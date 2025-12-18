# stock_comparison.py - 独立的收益率对比功能模块
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from config import PRESET_STOCKS, BENCHMARK_OPTIONS
# 复用主配置的股票列表（也可单独定义）


def show_stock_comparison():
    """
    股票收益率对比核心函数（供main.py调用）
    功能：选择两只股票，绘制同图收益率对比
    """
    st.subheader("📊 股票收益率对比分析")
    st.markdown("---")

    # 1. 对比参数配置（一行两列布局，加入卡片式美化）
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**基准标的（Stock A）**")
            # 第一只股票选择
            stock1 = st.selectbox(
                "第一只股票",
                options=["📝 手动输入"] + PRESET_STOCKS,
                key="comp_stock1",
                index=1  # 默认选AAPL
            )
            if stock1 == "📝 手动输入":
                stock1_code = st.text_input(
                    "股票代码", value="AAPL", key="comp_stock1_input").strip().upper()
            else:
                stock1_code = stock1.split(" - ")[0].strip().upper()

            # 时间周期选择
            period = st.selectbox(
                "时间周期",
                options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"],
                key="comp_period",
                index=3  # 默认1年
            )

    with col2:
        with st.container(border=True):
            st.markdown("**对比标的（Stock B）**")
            # 第二只股票选择
            stock2 = st.selectbox(
                "第二只股票",
                options=["📝 手动输入"] + PRESET_STOCKS,
                key="comp_stock2",
                index=2  # 默认选MSFT
            )
            if stock2 == "📝 手动输入":
                stock2_code = st.text_input(
                    "股票代码", value="MSFT", key="comp_stock2_input").strip().upper()
            else:
                stock2_code = stock2.split(" - ")[0].strip().upper()

            # 收益率类型选择
            return_type = st.radio(
                "收益率类型",
                options=["累计收益率", "每日收益率"],
                key="comp_return_type",
                horizontal=True
            )

    # 2. 数据获取与收益率计算（带缓存）
    @st.cache_data(ttl=3600)  # 缓存1小时，避免重复请求
    def get_stock_returns(ticker, period, return_type):
        """获取股票收益率数据"""
        try:
            # 下载调整后收盘价（考虑分红/拆股）
            df = yf.download(ticker, period=period,
                             progress=False)["Close"]
            if return_type == "累计收益率":
                # 累计收益率 = (当前价/初始价 - 1) * 100
                returns = (df / df.iloc[0] - 1) * 100
            else:
                # 每日收益率 = (当日价/前日价 - 1) * 100
                returns = df.pct_change() * 100
            return returns
        except Exception as e:
            st.error(f"获取 {ticker} 数据失败：{str(e)}")
            return None

    # 额外：可选基准指数
    benchmark_code = st.selectbox(
        "选择基准指数（可选）",
        options=["不对标"] + list(BENCHMARK_OPTIONS.keys()),
        format_func=lambda x: "不对标" if x == "不对标" else f"{x} - {BENCHMARK_OPTIONS.get(x, '')}",
        key="benchmark_code",
    )

    # 获取两只股票的收益率数据（用于图表展示）
    stock1_returns = get_stock_returns(stock1_code, period, return_type)
    stock2_returns = get_stock_returns(stock2_code, period, return_type)
    benchmark_returns = None
    if benchmark_code != "不对标":
        benchmark_returns = get_stock_returns(benchmark_code, period, return_type)

    # 额外：单独计算“每日收益率”序列，用于风险指标统计，避免对累计收益再累乘
    stock1_daily = get_stock_returns(stock1_code, period, "每日收益率")
    stock2_daily = get_stock_returns(stock2_code, period, "每日收益率")

    # 3. 绘制同图对比
    if stock1_returns is not None and stock2_returns is not None:
        # 对齐数据索引（避免时间维度不一致）
        combined_returns = pd.concat([stock1_returns, stock2_returns], axis=1)
        combined_returns.columns = [stock1_code, stock2_code]
        combined_returns = combined_returns.dropna()  # 删除缺失值

        # 如果有基准，拼接到同一DataFrame中
        if benchmark_returns is not None:
            combined_returns = pd.concat(
                [combined_returns, benchmark_returns], axis=1
            ).dropna()
            combined_returns.columns = [stock1_code, stock2_code, "Benchmark"]
        else:
            combined_returns = combined_returns.dropna()

        # 创建Plotly交互式图表
        fig = go.Figure()

        # 添加第一只股票曲线
        fig.add_trace(go.Line(
            x=combined_returns.index,
            y=combined_returns[stock1_code],
            name=stock1_code,
            line=dict(width=2, color="#1f77b4"),
            hovertemplate="日期：%{x}<br>收益率：%{y:.2f}%<extra></extra>"
        ))

        # 添加第二只股票曲线
        fig.add_trace(go.Line(
            x=combined_returns.index,
            y=combined_returns[stock2_code],
            name=stock2_code,
            line=dict(width=2, color="#ff7f0e"),
            hovertemplate="日期：%{x}<br>收益率：%{y:.2f}%<extra></extra>"
        ))

        # 可选添加基准曲线
        if benchmark_returns is not None and "Benchmark" in combined_returns.columns:
            fig.add_trace(go.Line(
                x=combined_returns.index,
                y=combined_returns["Benchmark"],
                name=f"Benchmark({benchmark_code})",
                line=dict(width=2, color="#6b7280", dash="dash"),
                hovertemplate="日期：%{x}<br>收益率：%{y:.2f}%<extra></extra>"
            ))

        # 添加0轴参考线（收益率基准）
        fig.add_hline(
            y=0, line_dash="dash", line_color="#888888", line_width=1,
            annotation_text="0%基准", annotation_position="bottom right"
        )

        # 图表样式优化
        title_suffix = f"{stock1_code} vs {stock2_code}"
        if benchmark_code != "不对标":
            title_suffix += f" vs {benchmark_code}"
        fig.update_layout(
            title=f"{title_suffix} - {return_type}对比（{period}）",
            xaxis_title="日期",
            yaxis_title=f"{return_type}（%）",
            legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)"),
            hovermode="x unified",
            height=600,
            template="plotly_white"
        )

        # 显示图表
        st.plotly_chart(fig, use_container_width=True)

        # 4. 关键统计信息展示（含风险指标）
        st.markdown("---")

        def calc_risk_stats(daily_series: pd.Series):
            """基于每日收益率序列计算风险指标。"""
            # 兼容传入 DataFrame 的情况：取第一列
            if isinstance(daily_series, pd.DataFrame):
                daily_series = daily_series.iloc[:, 0]

            ret = daily_series.dropna() / 100  # 转为小数
            if ret.empty:
                return None
            avg = ret.mean()
            vol = float(ret.std())
            ann_vol = vol * (252 ** 0.5)
            sharpe = None
            if vol != 0:
                sharpe = avg / vol * (252 ** 0.5)

            # 最大回撤
            cum = (1 + ret).cumprod()
            rolling_max = cum.cummax()
            drawdown = (cum - rolling_max) / rolling_max
            max_dd = drawdown.min()
            # 使用每日收益率累积得到最终收益率
            final = (1 + ret).prod() - 1
            return {
                "final": final,
                "avg": avg,
                "ann_vol": ann_vol,
                "sharpe": sharpe,
                "max_dd": max_dd,
            }

        stat1 = calc_risk_stats(stock1_daily) if stock1_daily is not None else None
        stat2 = calc_risk_stats(stock2_daily) if stock2_daily is not None else None

        col_stat1, col_stat2 = st.columns(2)
        if stat1:
            with col_stat1:
                st.markdown(f"### {stock1_code} 核心指标")
                st.metric("最终收益率", f"{stat1['final']*100:.2f}%")
                st.metric("平均日收益率", f"{stat1['avg']*100:.2f}%")
                st.metric("年化波动率", f"{stat1['ann_vol']*100:.2f}%")
                st.metric("最大回撤", f"{stat1['max_dd']*100:.2f}%")
        if stat2:
            with col_stat2:
                st.markdown(f"### {stock2_code} 核心指标")
                st.metric("最终收益率", f"{stat2['final']*100:.2f}%")
                st.metric("平均日收益率", f"{stat2['avg']*100:.2f}%")
                st.metric("年化波动率", f"{stat2['ann_vol']*100:.2f}%")
                st.metric("最大回撤", f"{stat2['max_dd']*100:.2f}%")

    else:
        st.warning("⚠️ 请检查股票代码是否正确（如AAPL、MSFT），或等待数据加载")
