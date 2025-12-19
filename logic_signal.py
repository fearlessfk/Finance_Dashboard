import pandas as pd

def get_investment_signal(df):
    try:
        signal_icon = "⚪"
        status = "无法判断"
        signal_reason = "数据不足，无法判断信号（需至少2行有效数据）"

        # ========== 关键修改：对齐实际列名 =========
        required_cols = ["RSI", "DIF", "DEA"]  # 替换为实际列名
        if not all(col in df.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in df.columns]
            signal_reason = f"缺少关键指标列：{missing_cols}（实际列名：RSI/DIF/DEA）"
            return signal_icon, status, signal_reason

        if len(df) < 1:
            return signal_icon, status, signal_reason

        # 重置为观望状态
        signal_icon = "🟡"
        status = "HOLD (观望)"
        signal_reason = ""

        # ========== 1. RSI 判断（列名一致，无需改） ==========
        rsi_value = df['RSI'].iloc[-1]
        if pd.isna(rsi_value):
            signal_reason = "RSI值无效（NaN）"
            return signal_icon, status, signal_reason
        
        if rsi_value > 75:
            status = "STRONG SELL (强烈卖出)"
            signal_icon = "🔴"
            signal_reason = f"RSI = {rsi_value:.1f} > 75（重度超买）"
        elif rsi_value > 70:
            status = "SELL (卖出)"
            signal_icon = "🟠"
            signal_reason = f"RSI = {rsi_value:.1f} > 70（轻度超买）"
        elif rsi_value < 25:
            status = "STRONG BUY (强烈买入)"
            signal_icon = "🟢"
            signal_reason = f"RSI = {rsi_value:.1f} < 25（重度超卖）"
        elif rsi_value < 30:
            status = "BUY (买入)"
            signal_icon = "🟣"
            signal_reason = f"RSI = {rsi_value:.1f} < 30（轻度超卖）"
        else:
            signal_reason = f"RSI = {rsi_value:.1f}（正常区间，30≤RSI≤70）"

        # ========== 2. MACD 交叉判断（替换列名：MACD→DIF，Signal_Line→DEA） ==========
        if len(df) >= 2:
            # 最新值（DIF对应原MACD，DEA对应原Signal_Line）
            dif_line = df['DIF'].iloc[-1]
            dea_line = df['DEA'].iloc[-1]
            if pd.isna(dif_line) or pd.isna(dea_line):
                signal_reason += "（MACD值无效）"
                return signal_icon, status, signal_reason
            
            # 前一日值
            prev_dif = df['DIF'].iloc[-2]
            prev_dea = df['DEA'].iloc[-2]

            # MACD金叉（DIF上穿DEA）
            if (prev_dif < prev_dea) and (dif_line > dea_line):
                macd_reason = f"MACD金叉（DIF={dif_line:.2f} 上穿DEA={dea_line:.2f}）"
                if "BUY" in status:
                    signal_reason += f" + {macd_reason}"
                elif "SELL" not in status:
                    status = "BUY (买入)"
                    signal_icon = "🟣"
                    signal_reason = macd_reason
            # MACD死叉（DIF下穿DEA）
            elif (prev_dif > prev_dea) and (dif_line < dea_line):
                macd_reason = f"MACD死叉（DIF={dif_line:.2f} 下穿DEA={dea_line:.2f}）"
                if "SELL" in status:
                    signal_reason += f" + {macd_reason}"
                elif "BUY" not in status:
                    status = "SELL (卖出)"
                    signal_icon = "🟠"
                    signal_reason = macd_reason
        else:
            signal_reason += "（数据不足，无法判断MACD交叉）"

        return signal_icon, status, signal_reason
    except Exception as e:
        return "❌", "错误", f"信号计算失败：{str(e)}"
