"""
基金波动分析数据获取模块
从同花顺获取场外基金趋势信号数据
"""
import requests
import json
from datetime import datetime


def get_fund_signal_data(code="015790", time_range="Month", signal_type="hexinrsi"):
    """
    获取基金趋势信号数据
    
    Args:
        code: 基金代码，默认 015790
        time_range: 时间范围，Month/Week/Year
        signal_type: 信号类型，hexinrsi
        
    Returns:
        字典格式的基金数据
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


def get_themes():
    """获取时间范围主题"""
    return {
        'Week': '近一周',
        'Month': '近一月',
        'Year': '近一年'
    }


if __name__ == '__main__':
    data = get_fund_signal_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
