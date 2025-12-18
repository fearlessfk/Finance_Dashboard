import plotly.graph_objects as go
import pandas as pd
from config import CHART_HEIGHT, SMA_WINDOW, SMA_COLOR
import mplfinance as mpf
from plotly.subplots import make_subplots

def plot_sma50(df):
    """绘制K线图+50日均线（原始代码中tab1的逻辑）"""
    
    fig = go.Figure()
    # 添加 K 线图（原始注释保留）
    fig.add_trace(go.Candlestick(
        x=df.index,  # K 线图的 x 轴为时间（数据中的索引，通常是日期或分钟级时间）（原始注释保留）
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='K线',
        increasing_line_color='#16a34a',  # 浅色主题下的上涨K线（绿色）
        decreasing_line_color='#dc2626'   # 浅色主题下的下跌K线（红色）
    ))  # go.Candlestick 是 Plotly 中专门用于绘制股票 K 线图的函数，K 线图能同时展示一个交易日的开盘价、最高价、最低价、收盘价，是股票分析的基础图表（原始注释保留）

    if len(df) > SMA_WINDOW:  # 只有当数据行数（交易日数量）大于 50 时，才绘制 50 日均线。（原始注释保留）
        # 添加 50 日均线（原始注释保留）
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50 (均线)', line=dict(color=SMA_COLOR)))
        # go.Scatter 是 Plotly 中绘制折线图的函数，这里用于绘制均线（一条平滑的趋势线）（原始注释保留）
        # mode='lines'：图表类型为折线图。（原始注释保留）
        fig.update_layout(
            height=CHART_HEIGHT,
            xaxis_rangeslider_visible=False,
            template="plotly_white",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color="#111827")
        )
        # xaxis_rangeslider_visible=False：关闭 x 轴的 “范围滑块”（默认会显示一个可拖动的滑块用于缩放时间范围）。关闭后图表更简洁，如需缩放可直接用鼠标滚轮。（原始注释保留）
        # height=600：图表高度设置为 600 像素。（原始注释保留）
    return fig


def plot_rsi(df):
    # 先过滤出买卖信号点
    buy_signals = df[df['RSI_Signal'] == 1]
    sell_signals = df[df['RSI_Signal'] == -1]

    # 双子图布局
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('股价走势', 'RSI指标（14期）- 买卖信号'),
        row_heights=[0.7, 0.3]
    )

    # 上半部分：K线+收盘价 + 买卖信号标注
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='K线'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Line(x=df.index, y=df['Close'], name='收盘价',
                line=dict(color='#1f77b4', width=1)),
        row=1, col=1
    )

    # 标注买入信号（绿色向上箭头）
    fig.add_trace(
        go.Scatter(
            x=buy_signals.index,
            y=buy_signals['Low'] * 0.98,  # 箭头位置在K线低点下方2%
            mode='markers+text',
            marker=dict(symbol='triangle-up', color='green', size=10),
            text='买入',
            textposition='bottom center',
            name='买入信号',
            textfont=dict(color='green', size=10)
        ),
        row=1, col=1
    )

    # 标注卖出信号（红色向下箭头）
    fig.add_trace(
        go.Scatter(
            x=sell_signals.index,
            y=sell_signals['High'] * 1.02,  # 箭头位置在K线高点上方2%
            mode='markers+text',
            marker=dict(symbol='triangle-down', color='red', size=10),
            text='卖出',
            textposition='top center',
            name='卖出信号',
            textfont=dict(color='red', size=10)
        ),
        row=1, col=1
    )

    # 下半部分：RSI + 超买超卖线 + 信号点
    fig.add_trace(
        go.Line(x=df.index, y=df['RSI'], name='RSI',
                line=dict(color='#ff7f0e')),
        row=2, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red",
                  row=2, col=1, annotation_text="超买线(70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green",
                  row=2, col=1, annotation_text="超卖线(30)")

    # RSI图中标注买入信号
    fig.add_trace(
        go.Scatter(
            x=buy_signals.index,
            y=buy_signals['RSI'],
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=8),
            name='RSI买入',
            showlegend=False
        ),
        row=2, col=1
    )

    # RSI图中标注卖出信号
    fig.add_trace(
        go.Scatter(
            x=sell_signals.index,
            y=sell_signals['RSI'],
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=8),
            name='RSI卖出',
            showlegend=False
        ),
        row=2, col=1
    )

    # 全局样式
    fig.update_layout(
        height=600,
        title="股价走势（RSI指标）- 买卖信号",
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1),
        template="plotly_white",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#111827")
    )
    fig.update_xaxes(rangeslider_visible=False)
    return fig


# logic_plot.py 中更新 plot_macd 函数
def plot_macd(df):
    # 过滤出金叉/死叉信号点
    golden_cross = df[df['MACD_Crossover'] == 1]  # 金叉（买入）
    death_cross = df[df['MACD_Crossover'] == -1]  # 死叉（卖出）

    # 双子图布局
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('股价走势', 'MACD指标 - 金叉/死叉信号'),
        row_heights=[0.7, 0.3]
    )

    # 上半部分：K线+收盘价 + 买卖信号标注
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='K线'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Line(x=df.index, y=df['Close'], name='收盘价',
                line=dict(color='#1f77b4', width=1)),
        row=1, col=1
    )

    # 标注金叉（买入）信号
    fig.add_trace(
        go.Scatter(
            x=golden_cross.index,
            y=golden_cross['Low'] * 0.98,
            mode='markers+text',
            marker=dict(symbol='triangle-up', color='green', size=10),
            text='金叉（买入）',
            textposition='bottom center',
            name='金叉',
            textfont=dict(color='green', size=10)
        ),
        row=1, col=1
    )

    # 标注死叉（卖出）信号
    fig.add_trace(
        go.Scatter(
            x=death_cross.index,
            y=death_cross['High'] * 1.02,
            mode='markers+text',
            marker=dict(symbol='triangle-down', color='red', size=10),
            text='死叉（卖出）',
            textposition='top center',
            name='死叉',
            textfont=dict(color='red', size=10)
        ),
        row=1, col=1
    )

    # 下半部分：MACD + 信号标注
    fig.add_trace(
        go.Line(x=df.index, y=df['DIF'], name='DIF',
                line=dict(color='#ff7f0e')),
        row=2, col=1
    )
    fig.add_trace(
        go.Line(x=df.index, y=df['DEA'],
                name='DEA', line=dict(color='#2ca02c')),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df['MACD_BAR'],
               name='MACD柱状图', marker_color='#d62728'),
        row=2, col=1
    )

    # MACD图中标注金叉点
    fig.add_trace(
        go.Scatter(
            x=golden_cross.index,
            y=golden_cross['DIF'],
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=8),
            name='MACD金叉',
            showlegend=False
        ),
        row=2, col=1
    )

    # MACD图中标注死叉点
    fig.add_trace(
        go.Scatter(
            x=death_cross.index,
            y=death_cross['DIF'],
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=8),
            name='MACD死叉',
            showlegend=False
        ),
        row=2, col=1
    )

    # 全局样式
    fig.update_layout(
        height=600,
        title="股价走势（MACD指标）- 金叉死叉信号",
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1),
        template="plotly_white",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#111827")
    )
    fig.update_xaxes(rangeslider_visible=False)
    return fig
