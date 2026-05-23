"""
宽基指数趋势大模型 - EMA版本 - 数据获取模块
逸飞ETF量化

指标计算（使用EMA指数移动平均）：
- 趋势线: (最高价 + 最低价) / 2 的20日指数移动平均(EMA)
- 偏离率: (现价 - 趋势线) / 趋势线 × 100%
- 强度排序: 按偏离率数值排序，数值最大=1（最强）

EMA特点：
- 更重视近期数据，反应更灵敏
- alpha = 2 / (period + 1) = 2/21 ≈ 0.0952
"""
import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_stock_data(stock_code: str, days: int = 100, end_date: str = None) -> pd.DataFrame:
    """获取股票/指数数据"""
    bs.login()
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=days)).strftime('%Y-%m-%d')
    
    rs = bs.query_history_k_data_plus(
        stock_code,
        'date,code,open,high,low,close,volume',
        start_date=start_date,
        end_date=end_date,
        frequency='d'
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    bs.logout()
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def calculate_indicators_ema(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """
    计算趋势线指标（使用EMA指数移动平均）
    
    公式：
    1. 均价 = (最高价 + 最低价) / 2
    2. 趋势线 = 均价的20日指数移动平均(EMA)
       EMA_t = alpha × price_t + (1-alpha) × EMA_{t-1}
       alpha = 2 / (period + 1) = 2/21 ≈ 0.0952
    """
    # 计算 (最高价 + 最低价) / 2
    df['hl2'] = (df['high'] + df['low']) / 2
    
    # 计算20日指数移动平均(EMA)
    # adjust=False 表示使用标准的递归 EMA 计算
    df['trend_line'] = df['hl2'].ewm(span=period, adjust=False).mean()
    
    # 计算偏离率
    df['deviation'] = (df['close'] - df['trend_line']) / df['trend_line'] * 100
    
    return df


def analyze_index(stock_code: str, period: int = 20) -> dict:
    """分析单只指数/股票"""
    try:
        df = get_stock_data(stock_code, days=period * 4)
        df = calculate_indicators_ema(df, period)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        today_change = (latest['close'] - prev['close']) / prev['close'] * 100
        
        change_5d = 0
        change_20d = 0
        if len(df) > 5:
            change_5d = (df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6] * 100
        if len(df) > 20:
            change_20d = (df['close'].iloc[-1] - df['close'].iloc[-21]) / df['close'].iloc[-21] * 100
        
        # 判断信号
        dev = latest['deviation']
        if dev > 5:
            signal = '极强'
            signal_class = 'signal-extreme-strong'
        elif dev > 2:
            signal = '强势'
            signal_class = 'signal-strong'
        elif dev > 0:
            signal = '偏强'
            signal_class = 'signal-mild-strong'
        elif dev > -2:
            signal = '偏弱'
            signal_class = 'signal-mild-weak'
        else:
            signal = '超卖'
            signal_class = 'signal-weak'
        
        return {
            'code': stock_code,
            'current_price': latest['close'],
            'trend_line': latest['trend_line'],
            'deviation': dev,
            'today_change': today_change,
            'change_5d': change_5d,
            'change_20d': change_20d,
            'signal': signal,
            'signal_class': signal_class,
        }
        
    except Exception as e:
        return {'code': stock_code, 'error': str(e)}


def get_index_list():
    """获取指数列表"""
    return [
        # A股主要指数
        {'code': 'sh.000001', 'name': '上证指数', 'category': 'A股指数'},
        {'code': 'sz.399001', 'name': '深证成指', 'category': 'A股指数'},
        {'code': 'sz.399006', 'name': '创业板指', 'category': 'A股指数'},
        
        # 宽基ETF
        {'code': 'sh.510050', 'name': '上证50', 'category': '宽基ETF'},
        {'code': 'sh.510300', 'name': '沪深300', 'category': '宽基ETF'},
        {'code': 'sh.510500', 'name': '中证500', 'category': '宽基ETF'},
        {'code': 'sh.512100', 'name': '中证1000', 'category': '宽基ETF'},
        {'code': 'sh.563300', 'name': '国证2000', 'category': '宽基ETF'},
        
        # 风格/策略ETF
        {'code': 'sz.159949', 'name': '创业板50', 'category': '风格ETF'},
        {'code': 'sz.159967', 'name': '创成长', 'category': '风格ETF'},
        {'code': 'sh.588000', 'name': '科创50', 'category': '风格ETF'},
        {'code': 'sh.588220', 'name': '科创100', 'category': '风格ETF'},
        {'code': 'sh.512890', 'name': '红利低波', 'category': '风格ETF'},
        
        # 跨境ETF（QDII）
        {'code': 'sz.159920', 'name': '恒生ETF', 'category': '跨境ETF'},
        {'code': 'sh.513130', 'name': '恒生科技', 'category': '跨境ETF'},
        {'code': 'sh.513100', 'name': '纳指ETF', 'category': '跨境ETF'},
        {'code': 'sh.513030', 'name': '德国ETF', 'category': '跨境ETF'},
        {'code': 'sh.513520', 'name': '日经ETF', 'category': '跨境ETF'},
        {'code': 'sh.513310', 'name': '中韩半导体', 'category': '跨境ETF'},
        {'code': 'sz.164824', 'name': '印度基金', 'category': '跨境ETF'},
        
        # 商品ETF
        {'code': 'sh.518880', 'name': '黄金ETF', 'category': '商品ETF'},
        {'code': 'sz.161226', 'name': '白银', 'category': '商品ETF'},
        {'code': 'sz.159985', 'name': '豆粕', 'category': '商品ETF'},
        {'code': 'sz.162411', 'name': '华宝油气', 'category': '商品ETF'},
    ]


def get_broad_index_data():
    """获取所有宽基指数数据"""
    index_list = get_index_list()
    results = []
    
    for index_info in index_list:
        try:
            result = analyze_index(index_info['code'])
            result['name'] = index_info['name']
            result['category'] = index_info['category']
            results.append(result)
        except Exception as e:
            print(f'Error analyzing {index_info["name"]}: {e}')
    
    # 过滤掉有错误的结果
    valid_results = [r for r in results if 'error' not in r]
    
    # 按偏离率排序（从高到低）
    valid_results.sort(key=lambda x: x.get('deviation', 0), reverse=True)
    
    # 添加强度排名
    for i, r in enumerate(valid_results, 1):
        r['rank'] = i
    
    return {
        'success': True,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'indices': valid_results,
    }


if __name__ == "__main__":
    data = get_broad_index_data()
    print(f"获取了 {len(data['indices'])} 个指数数据")
    for i, idx in enumerate(data['indices'][:5], 1):
        print(f"{i}. {idx['name']}: 偏离率 {idx['deviation']:.2f}%, {idx['signal']}")
