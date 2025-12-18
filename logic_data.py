import streamlit as st
import yfinance as yf
import pandas as pd
import os
from config import PROXY_HTTP, PROXY_HTTPS, CACHE_TTL

# 设置环境变量，让 Python 走你的本地代理（原始代码逻辑）
os.environ["http_proxy"] = PROXY_HTTP
os.environ["https_proxy"] = PROXY_HTTPS


@st.cache_data(ttl=CACHE_TTL)  # 1小时缓存，减少请求（原始注释保留）
def get_data(symbol, period):
    # 初始化返回值，确保即使报错也有值（原始注释保留）
    hist_df = pd.DataFrame()
    info = {}
    news = []
    try:
        # 函数内局部变量stock，外部无需访问（原始注释保留）
        stock_inner = yf.Ticker(symbol)
        hist_df = stock_inner.history(period=period)
        info = stock_inner.info or {}  # 确保info是字典（原始注释保留）
        news = stock_inner.news or []  # 确保news是列表（原始注释保留）
    except Exception as e:
        st.error(f"数据获取失败：{str(e)}")  # 页面显示错误原因（原始注释保留）
    return hist_df, info, news


def get_balance_sheet(ticker_symbol):
    """获取资产负债表（原始代码中tab3的逻辑）"""
    try:
        # 重新初始化 Ticker 对象以获取资产负债表（避免缓存问题）（原始注释保留）
        stock_inner = yf.Ticker(ticker_symbol)
        # 获取股票的资产负债表数据（原始注释保留）
        balance_sheet = stock_inner.balance_sheet
        return balance_sheet
    except Exception as e:
        st.warning(f"获取资产负债表失败：{str(e)}")  # 原始容错逻辑
        return pd.DataFrame()
