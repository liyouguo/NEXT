"""
基金波动分析数据获取模块
从同花顺获取场外基金趋势信号数据
支持参数化基金池和自动查询特定标的
"""
import requests
import json
from datetime import datetime

# =====================
# 基金池配置
# =====================
DEFAULT_FUND_POOL = [
    {'code': '015790', 'name': '广发中证军工ETF联接A'},
    {'code': '005911', 'name': '广发双擎升级混合A'},
    {'code': '161725', 'name': '招商中证白酒指数(LOF)A'},
    {'code': '007339', 'name': '易方达中小盘混合'},
    {'code': '005827', 'name': '易方达蓝筹精选混合'},
]


def get_fund_pool():
    """
    获取预设基金池
    
    Returns:
        list: 基金池列表，每个元素包含code和name
    """
    return DEFAULT_FUND_POOL


def get_fund_signal_data(code="015790", time_range="Month", signal_type="hexinrsi"):
    """
    获取基金趋势信号数据
    
    Args:
        code: 基金代码，默认 015790
        time_range: 时间范围，Month/Week/Year
        signal_type: 信号类型，hexinrsi
        
    Returns:
        dict: 基金数据或错误信息
    """
    url = "https://dq.10jqka.com.cn/fuyao/fund_fe_components/fund_performance_trend/v1/signal_statistics"
    
    payload = {
        "code": code,
        "config": {
            "authorityJumpUrl": "https://mams.10jqka.com.cn/new/server/html/64259.html?injectAdaptive=true",
            "isShowDashBoard": "1",
            "robotText": "点击查看今日信号 >",
            "unauthorityJumpUrl": "https://mams.10jqka.com.cn/new/server/html/61961.html"
        },
        "timeRange": time_range,
        "type": signal_type,
        "authority": True
    }
    
    headers = {
        'User-Agent': "IphoneIJiJinSDK/7.43.01",
        'Content-Type': "application/json",
        'Accept-Language': "zh-Hans-CN;q=1, en-CN;q=0.9"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        data = response.json()
        
        status_code = data.get('status_code', -1)
        status_msg = data.get('status_msg', '')
        
        if status_code == 0 and status_msg == 'ok':
            result = data.get('data', {})
            rsi_level = result.get('rsiLevelStatus', '0')
            config = result.get('dashBoardRenderConfig', {})
            signal_text = config.get('robotText', '').replace('<span>', '').replace('</span>', '')
            data_list = config.get('dataList', [])
            
            # 计算RSI数值（根据级别0-4对应20-80
            rsi_value_map = {
                '0': 20,
                '1': 35,
                '2': 50,
                '3': 65,
                '4': 80
            }
            rsi_value = rsi_value_map.get(rsi_level, 50)
            
            level_map = {
                '0': {'name': '极低', 'desc': '超卖区域', 'class': 'level-low'},
                '1': {'name': '较低', 'desc': '偏低区域', 'class': 'level-medium-low'},
                '2': {'name': '中等', 'desc': '中间水平', 'class': 'level-medium'},
                '3': {'name': '较高', 'desc': '偏高区域', 'class': 'level-medium-high'},
                '4': {'name': '极高', 'desc': '超买区域', 'class': 'level-high'}
            }
            
            level_info = level_map.get(rsi_level, {'name': '未知', 'desc': '未知区域', 'class': 'level-unknown'})
            
            formatted_data = {
                'code': code,
                'queryTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'rsiLevel': rsi_level,
                'rsiValue': rsi_value,
                'levelName': level_info['name'],
                'levelDesc': level_info['desc'],
                'levelClass': level_info['class'],
                'signalText': signal_text,
                'dataList': []
            }
            
            for idx, item in enumerate(data_list):
                title = item.get('title', '')
                value = item.get('value', '')
                color = item.get('color', '')
                
                trend = 'neutral'
                if 'FF2436' in color or '+' in value:
                    trend = 'up'
                elif 'rgba(0,0,0' in color:
                    trend = 'neutral'
                else:
                    trend = 'down'
                
                formatted_data['dataList'].append({
                    'id': idx,
                    'title': title,
                    'value': value,
                    'color': color,
                    'trend': trend
                })
            
            return formatted_data
        else:
            return {'error': status_msg, 'errorCode': status_code}
            
    except Exception as e:
        return {'error': str(e), 'errorCode': -1}


def get_batch_fund_signals(fund_codes=None, time_range="Month", signal_type="hexinrsi"):
    """
    批量查询多个基金的信号数据
    
    Args:
        fund_codes: 基金代码列表，如果为None则使用默认基金池
        time_range: 时间范围，Month/Week/Year
        signal_type: 信号类型，hexinrsi
        
    Returns:
        dict: 包含所有基金数据的字典，key为基金代码，value为对应数据
    """
    # 如果没有指定基金代码，使用默认基金池
    if fund_codes is None:
        fund_pool = get_fund_pool()
        fund_codes = [fund['code'] for fund in fund_pool]
    
    results = {}
    for code in fund_codes:
        result = get_fund_signal_data(code, time_range, signal_type)
        results[code] = result
    
    return results


def get_themes():
    """
    获取时间范围主题
    
    Returns:
        dict: 时间范围显示名称映射
    """
    return {
        'Week': '近一周',
        'Month': '近一月',
        'Year': '近一年'
    }


if __name__ == '__main__':
    # 测试单个基金查询
    print("=== 测试单个基金查询 ===")
    data = get_fund_signal_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    print("\n=== 测试批量基金查询 ===")
    batch_data = get_batch_fund_signals()
    print(f"共查询 {len(batch_data)} 只基金")
    for code, result in batch_data.items():
        print(f"\n基金 {code}:")
        print(f"  RSI级别: {result.get('levelName', '未知')}")