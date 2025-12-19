import streamlit as st
import yfinance as yf
import pandas as pd
import time
import random
from config import CACHE_TTL


@st.cache_data(ttl=CACHE_TTL)  # 1小时缓存，减少请求（原始注释保留）
def get_data(symbol, period):
    # 初始化返回值，确保即使报错也有值（原始注释保留）
    hist_df = pd.DataFrame()
    info = {}
    news = []
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 函数内局部变量stock，外部无需访问（原始注释保留）
            stock_inner = yf.Ticker(symbol)
            hist_df = stock_inner.history(period=period)
            info = stock_inner.info or {}  # 确保info是字典（原始注释保留）
            news = stock_inner.news or []  # 确保news是列表（原始注释保留）
            break  # 成功则跳出循环
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # 指数退避 + 随机
                    st.warning(f"请求过于频繁，正在重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    st.error(f"数据获取失败：请求过于频繁，请稍后再试。错误详情：{str(e)}")
            else:
                st.error(f"数据获取失败：{str(e)}")
                break
    return hist_df, info, news


def get_balance_sheet(ticker_symbol):
    """获取资产负债表（原始代码中tab3的逻辑）"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 重新初始化 Ticker 对象以获取资产负债表（避免缓存问题）（原始注释保留）
            stock_inner = yf.Ticker(ticker_symbol)
            # 获取股票的资产负债表数据（原始注释保留）
            balance_sheet = stock_inner.balance_sheet
            return balance_sheet
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    st.warning(f"资产负债表请求过于频繁，正在重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    st.warning(f"获取资产负债表失败：请求过于频繁，请稍后再试。错误详情：{str(e)}")
                    return pd.DataFrame()
            else:
                st.warning(f"获取资产负债表失败：{str(e)}")  # 原始容错逻辑
                return pd.DataFrame()
    return pd.DataFrame()
