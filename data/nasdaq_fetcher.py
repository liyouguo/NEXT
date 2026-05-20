"""
NASDAQ 指数数据获取模块
独立模块，负责从天天基金 API 获取纳斯达克数据
"""

import requests
import json


def fetch_nasdaq_data(index_code="IXIC", company_code="80000226", date_range="3y"):
    """
    抓取天天基金指数历史数据
    
    参数:
        index_code: 指数代码，默认 IXIC (纳斯达克综合指数)
        company_code: 机构代码，默认 80000226
        date_range: 时间范围，默认 3y (3年)
    
    返回:
        dict: API 返回的完整数据
    """
    url = "https://fundcomapi.tiantianfunds.com/mm/FundIndex/CompanyIndexSeries"
    params = {
        'COMPANYCODE': company_code,
        'FIELDS': "INDEXCODE,COMPANYCODE,PDATE,CLOSE,SIGNALSCORE",
        'INDEXCODE': index_code,
        'RANGE': date_range
    }
    headers = {
        'User-Agent': "EMProjJijin/6.8.6 (iPhone; iOS 26.2.1; Scale/3.00)",
        'GTOKEN': "20A0CC6678754765B64BA6387AAD6582",
        'clientInfo': "ttjj-iPhone 16 Pro Max-iOS-iOS26.2.1",
        'MP-VERSION': "1.1.0",
        'tracestate': "pid=0x106d8dfc0,taskid=0x14f9d1ec0",
        'Accept-Language': "zh-Hans-CN;q=1, en-CN;q=0.9",
        'Referer': "https://mpservice.com/fundfe49d55f6b214d/release/pages/index",
        'traceparent': "00-cc8a536ab4ba442f982889ad7a2db8ae-0000000000000000-01"
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_nasdaq_chart_data():
    """
    获取用于图表展示的 NASDAQ 数据（主入口函数）
    
    返回:
        list: 格式化后的数据列表
    """
    data = fetch_nasdaq_data()
    return data.get('data', [])


if __name__ == "__main__":
    data = get_nasdaq_chart_data()
    print(data)
    print(f"获取到 {len(data)} 条 NASDAQ 数据")
