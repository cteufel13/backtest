import pandas as pd
import numpy as np


metrics = {
    "Start": "Start",
    "End": "End",
    "Duration": "Duration",
    "Exposure Time [%]": "ExposureTime",
    "Equity Final [$]": "EquityFinal",
    "Equity Peak [$]": "EquityPeak",
    "Return [%]": "ReturnPct",
    "Buy & Hold Return [%]": "BuyHoldReturn",
    "Return (Ann.) [%]": "ReturnAnn",
    "Volatility (Ann.) [%]": "VolatilityAnn",
    "CAGR [%]": "Cagr",
    "Sharpe Ratio": "SharpeRatio",
    "Sortino Ratio": "SortinoRatio",
    "Max. Drawdown [%]": "MaxDrawdown",
    "Avg. Drawdown [%]": "AvgDrawdown",
    "# Trades": "Trades",
    # "Win Rate [%]": "WinRate",
    # "Best Trade [%]": "BestTrade",
    # "Worst Trade [%]": "WorstTrade",
    # "Avg. Trade Duration": "AvgTradeDuration",
    # "Avg. Trade Return [%]": "AvgTradeReturn",
    # "Profit Factor": "ProfitFactor",
    # "Expectancy [%]": "Expectancy",
    # "SQN": "SQN",
    # "Kelly Criterion": "KellyCriterion",
    # "_strategy": "Strategy"
}

def get_performance_metrics()->list:
    return list(metrics.keys())

def calculate_metrics(date,results_df: pd.DataFrame, action_data) -> pd.Series:
    """
    Calculate all trading metrics and return them as a single pandas Series.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing all trading results
        
    Returns:
        pd.Series: All calculated metrics in a single row
    """
    metrics = {
        "Date": date,
        "Start": calculate_Start(results_df),
        "End": calculate_End(results_df),
        "Duration": calculate_Duration(results_df),
        "Exposure Time [%]": calculate_ExposureTime(results_df),
        "Equity Final [$]": calculate_EquityFinal(results_df),
        "Equity Peak [$]": calculate_EquityPeak(results_df),
        "Return [%]": calculate_ReturnPct(results_df),
        "Buy & Hold Return [%]": calculate_BuyHoldReturn(results_df),
        "Return (Ann.) [%]": calculate_ReturnAnn(results_df),
        "Volatility (Ann.) [%]": calculate_VolatilityAnn(results_df),
        "CAGR [%]": calculate_Cagr(results_df),
        "Sharpe Ratio": calculate_SharpeRatio(results_df),
        "Sortino Ratio": calculate_SortinoRatio(results_df),
        "Max. Drawdown [%]": calculate_MaxDrawdown(results_df),
        "Avg. Drawdown [%]": calculate_AvgDrawdown(results_df),
        "# Trades": calculate_Trades(results_df,action_data),
        # "Win Rate [%]": calculate_WinRate(results_df),
        # "Best Trade [%]": calculate_BestTrade(results_df),
        # "Worst Trade [%]": calculate_WorstTrade(results_df),
        # "Avg. Trade Duration": calculate_AvgTradeDuration(results_df),
        # "Avg. Trade Return [%]": calculate_AvgTradeReturn(results_df),
        # "Profit Factor": calculate_ProfitFactor(results_df),
        # "Expectancy [%]": calculate_Expectancy(results_df),
        # "SQN": calculate_SQN(results_df),
        # "Kelly Criterion": calculate_sKellyCriterion(results_df),
        # "_strategy": calculate_Strategy(results_df.get('_strategy', 'Unknown'))
    }
    
    return pd.Series(metrics)  


def calculate_Start(results_df: pd.DataFrame):
    """Get the start date of the backtest"""
    try:
        return results_df.index[0]
    except:
        pass

def calculate_End(results_df: pd.DataFrame):
    """Get the end date of the backtest"""
    try:
        return results_df.index[-1]
    except:
        pass

def calculate_Duration(results_df: pd.DataFrame):
    """Calculate the total duration of the backtest"""
    try:
        return results_df.index[-1] - results_df.index[0]
    except:
        pass

def calculate_ExposureTime(results_df: pd.DataFrame):
    """
    Calculate the percentage of time the strategy is invested in the market.
    Considers times when there are active positions.
    """
    # Check if we have any positions by seeing if there's a difference
    # between portfolio value and cash (accounting for small float differences)
    has_positions = (results_df['Portfolio Value'] - results_df['Cash']).abs() > 0.01
    total_periods = len(results_df)
    return (has_positions.sum() / total_periods) * 100

def calculate_EquityFinal(results_df: pd.DataFrame):
    """Calculate the final equity value"""
    return results_df['Equity'].iloc[-1]

def calculate_EquityPeak(results_df: pd.DataFrame):
    """Calculate the peak equity value"""
    return results_df['Equity'].max()

def calculate_ReturnPct(results_df: pd.DataFrame):
    """Calculate the total return percentage"""
    initial_capital = results_df['Capital'].iloc[0]
    final_equity = results_df['Equity'].iloc[-1]
    return ((final_equity - initial_capital) / initial_capital) * 100

def calculate_BuyHoldReturn(results_df: pd.DataFrame):
    """
    Calculate buy and hold return percentage for each stock and return the average
    """
    buy_hold_returns = []
    for ticker in results_df['Stock Info'].iloc[0].keys():
        first_price = results_df['Stock Info'].iloc[0][ticker]['Close']
        last_price = results_df['Stock Info'].iloc[-1][ticker]['Close']
        buy_hold_return = ((last_price - first_price) / first_price) * 100
        buy_hold_returns.append(buy_hold_return)
    return np.mean(buy_hold_returns)

def calculate_ReturnAnn(results_df: pd.DataFrame):
    """Calculate annualized return percentage"""
    # Ensure the index is in datetime format
    results_df.index = pd.to_datetime(results_df.index)

    # print(results_df.index[-1], results_df.index[0], results_df.index[-1] - results_df.index[0])
    total_days = (results_df.index[-1] - results_df.index[0]).days
    total_return = calculate_ReturnPct(results_df) / 100  # Convert percentage to decimal
    if total_days == 0:
        return 0
    return (((1 + total_return) ** (365 / total_days)) - 1) * 100

def calculate_VolatilityAnn(results_df: pd.DataFrame):
    """Calculate annualized volatility"""
    daily_returns = results_df['Equity'].pct_change()
    return np.std(daily_returns.dropna()) * np.sqrt(252) * 100

def calculate_Cagr(results_df: pd.DataFrame):
    """Calculate Compound Annual Growth Rate"""
    return calculate_ReturnAnn(results_df)

def calculate_SharpeRatio(results_df: pd.DataFrame, risk_free_rate=0.02):
    """Calculate Sharpe Ratio using daily returns"""
    daily_returns = results_df['Equity'].pct_change()
    excess_returns = daily_returns - (risk_free_rate/252)  # Convert annual risk-free rate to daily
    if excess_returns.std() == 0:
        return 0
    return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())

def calculate_SortinoRatio(results_df: pd.DataFrame, risk_free_rate=0.02):
    """Calculate Sortino Ratio using daily returns"""
    daily_returns = results_df['Equity'].pct_change()
    excess_returns = daily_returns - (risk_free_rate/252)
    downside_returns = excess_returns[excess_returns < 0]
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0
    return np.sqrt(252) * (excess_returns.mean() / downside_returns.std())

def calculate_MaxDrawdown(results_df: pd.DataFrame):
    """Calculate Maximum Drawdown percentage"""
    equity = results_df['Equity']
    peak = equity.expanding(min_periods=1).max()
    drawdown = ((equity - peak) / peak) * 100
    return abs(drawdown.min())

def calculate_AvgDrawdown(results_df: pd.DataFrame):
    """Calculate Average Drawdown percentage"""
    equity = results_df['Equity']
    peak = equity.expanding(min_periods=1).max()
    drawdowns = ((equity - peak) / peak) * 100
    negative_drawdowns = drawdowns[drawdowns < 0]
    return abs(negative_drawdowns.mean()) if len(negative_drawdowns) > 0 else 0

def calculate_Trades(results_df: pd.DataFrame,action_data):
    """Calculate total number of trades"""  
    trade_count = 0

    trade_count += sum(1 for entry in action_data['Type'] if entry in ['buy', 'sell'])
    return trade_count

def calculate_WinRate(results_df: pd.DataFrame):
    """Calculate Win Rate percentage"""
    winning_trades = 0
    total_trades = 0
    
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell':
                    total_trades += 1
                    if hasattr(action, 'pnl') and action.pnl > 0:
                        winning_trades += 1
    
    return (winning_trades / total_trades * 100) if total_trades > 0 else 0

def calculate_BestTrade(results_df: pd.DataFrame):
    """Calculate Best Trade return percentage"""
    trade_returns = []
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell' and hasattr(action, 'pnl'):
                    trade_returns.append(action.pnl)
    return max(trade_returns) if trade_returns else 0

def calculate_WorstTrade(results_df: pd.DataFrame):
    """Calculate Worst Trade return percentage"""
    trade_returns = []
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell' and hasattr(action, 'pnl'):
                    trade_returns.append(action.pnl)
    return min(trade_returns) if trade_returns else 0

def calculate_AvgTradeDuration(results_df: pd.DataFrame):
    """Calculate Average Trade Duration"""
    durations = []
    open_positions = {}
    
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'buy':
                    open_positions[action.ticker] = row.Index
                elif action.type == 'sell' and action.ticker in open_positions:
                    duration = row.Index - open_positions[action.ticker]
                    durations.append(duration)
                    del open_positions[action.ticker]
    
    return pd.Timedelta(sum(durations, pd.Timedelta(0)) / len(durations)) if durations else pd.Timedelta(0)

def calculate_AvgTradeReturn(results_df: pd.DataFrame):
    """Calculate Average Trade Return percentage"""
    trade_returns = []
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell' and hasattr(action, 'pnl'):
                    trade_returns.append(action.pnl)
    return np.mean(trade_returns) if trade_returns else 0

def calculate_ProfitFactor(results_df: pd.DataFrame):
    """Calculate Profit Factor"""
    winning_trades = []
    losing_trades = []
    
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell' and hasattr(action, 'pnl'):
                    if action.pnl > 0:
                        winning_trades.append(action.pnl)
                    else:
                        losing_trades.append(abs(action.pnl))
    
    total_wins = sum(winning_trades)
    total_losses = sum(losing_trades)
    
    return total_wins / total_losses if total_losses != 0 else float('inf')

def calculate_Expectancy(results_df: pd.DataFrame):
    """Calculate Strategy Expectancy"""
    trade_returns = []
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell' and hasattr(action, 'pnl'):
                    trade_returns.append(action.pnl)
    
    if not trade_returns:
        return 0
    
    win_rate = sum(1 for x in trade_returns if x > 0) / len(trade_returns)
    avg_win = np.mean([x for x in trade_returns if x > 0]) if any(x > 0 for x in trade_returns) else 0
    avg_loss = abs(np.mean([x for x in trade_returns if x < 0])) if any(x < 0 for x in trade_returns) else 0
    
    return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

def calculate_SQN(results_df: pd.DataFrame):
    """Calculate System Quality Number"""
    trade_returns = []
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell' and hasattr(action, 'pnl'):
                    trade_returns.append(action.pnl)
    
    if not trade_returns or np.std(trade_returns) == 0:
        return 0
        
    return (np.mean(trade_returns) * np.sqrt(len(trade_returns))) / np.std(trade_returns)

def calculate_KellyCriterion(results_df: pd.DataFrame):
    """Calculate Kelly Criterion"""
    trade_returns = []
    for row in results_df.itertuples():
        if hasattr(row, 'Action') and row.Action:
            for action in row.Action:
                if action.type == 'sell' and hasattr(action, 'pnl'):
                    trade_returns.append(action.pnl)
    
    if not trade_returns:
        return 0
    
    win_rate = sum(1 for x in trade_returns if x > 0) / len(trade_returns)
    avg_win = np.mean([x for x in trade_returns if x > 0]) if any(x > 0 for x in trade_returns) else 0
    avg_loss = abs(np.mean([x for x in trade_returns if x < 0])) if any(x < 0 for x in trade_returns) else 0
    
    if avg_win == 0 or avg_loss == 0:
        return 0
        
    return ((win_rate * avg_win) - ((1 - win_rate) * avg_loss)) / avg_win

def calculate_Strategy(strategy_name: str):
    """Return strategy name"""
    return strategy_name