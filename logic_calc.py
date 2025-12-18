import pandas as pd


def calc_price_metrics(df):
    """计算价格涨跌幅（原始代码中col1-col3的逻辑）"""
    if len(df) > 1:
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        delta = current_price - prev_price
        delta_percent = (delta/prev_price)*100
        return current_price, delta, delta_percent
    return None, None, None


def calc_sma_50(df):
    """计算50日简单移动平均线（原始代码中tab1的逻辑）"""
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    return df


def calc_RSI(df, period=14):
    """计算相对强弱指数RSI（新增功能）"""
    delta = df['Close'].diff()
    delta = delta.dropna()  # 计算每日价格变动,参数为1表示计算当前行与前一行的差值，默认是1
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi

    # 生成RSI买卖信号
    df['RSI_Signal'] = 0  # 0=无信号，1=买入，-1=卖出
    df.loc[df['RSI'] < 30, 'RSI_Signal'] = 1    # 超卖→买入
    df.loc[df['RSI'] > 70, 'RSI_Signal'] = -1   # 超买→卖出

    return df


def calc_MACD(df, short_window=12, long_window=26, signal_window=9):
    """计算移动平均收敛散度指标MACD（新增功能）"""
    exp1 = df['Close'].ewm(span=short_window, adjust=False).mean()
    exp2 = df['Close'].ewm(span=long_window, adjust=False).mean()
    DIF = exp1 - exp2
    DEA = DIF.ewm(span=signal_window, adjust=False).mean()
    df['DIF'] = DIF
    df['DEA'] = DEA
    df['MACD_BAR'] = 2 * (DIF - DEA)

    # 生成MACD买卖信号（金叉/死叉）
    df['MACD_Crossover'] = 0  # 0=无信号，1=金叉（买入），-1=死叉（卖出）
    # 金叉：DIF上穿DEA（前一天DIF<DEA，当天DIF>DEA）
    df.loc[(df['DIF'].shift(1) < df['DEA'].shift(1)) &
           (df['DIF'] > df['DEA']), 'MACD_Crossover'] = 1
    # 死叉：DIF下穿DEA（前一天DIF>DEA，当天DIF<DEA）
    df.loc[(df['DIF'].shift(1) > df['DEA'].shift(1)) &
           (df['DIF'] < df['DEA']), 'MACD_Crossover'] = -1
    

    return df


