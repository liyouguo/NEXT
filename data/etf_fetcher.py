"""
ETF 上升趋势数据获取模块
独立模块，负责从同花顺 API 获取 ETF 数据
主要功能：
1. 获取上升趋势ETF列表
2. 获取ETF详情指标（涨幅、趋势、涨停等）
3. 获取AI洞察标签
4. 数据排序功能
"""

import requests
import json
from datetime import datetime

# ============ 配置区（Cookie过期需更新） ============
# 注意：Cookie可能会过期，需要定期从浏览器中复制更新
POOL_COOKIE = "v=A-hg3lGuFXCmUTn0KVen6KGHvdz_EUwbLnUgn6IZNGNW_YfDSiEcq36F8C3x; _clsk=he4oka%7C1778084894694%7C2%7C1%7C; _clck=1x2613x%7C2%7Cg5t%7C0%7C0; IFUserCookieKey={\"userid\":\"438819001\",\"escapename\":\"%25u6715%25u7684%25u540e%25u5bab%25u53ea%25u6709\",\"custid\":\"100121177685\"}; cuc=1eab8703c6d74d3a8e8b1eb20d0f35b3; sess_tk=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6InNlc3NfdGtfMSIsImJ0eXAiOiJzZXNzX3RrcyJ9.eyJqdGkiOiI0M2FiODMzNTMzMzBmZWZhMmE0ZWFkZjIyMDJjZWQ5ZDEiLCJpYXQiOjE3NzYzMTIyMTgsImV4cCI6MTc3ODk5MDYxOCwic3ViIjoiNDM4ODE5MDAxIiwiaXNzIjoidXBhc3MuMTBqcWthLmNvbS5jbiIsImF1ZCI6IjIwMjMwODA0OTA3NTEyOTIiLCJhY3QiOiJvZmMiLCJjdWhzIjoiYWJjNTZlZjlkYmRlMGE1NGQyZDAzYWI3MDhkMGRkOGU2ODAxZjIzMmRkNmZhOGY5Y2MyMTI5Mzg3NjZhOTZlYiJ9.02HQMVj_an7DPvdcmhnOVuWpNpM_rFMe_zIGbGoHXFWZ4lCNA5y29k7rFNjo2bcyqj1oW4hbERZmRdri41GO4g; ticket=80fdc178173ecb806504deee82ed27f5; u_name=%EB%DE%B5%C4%BA%F3%B9%AC%D6%BB%D3%D0; user=MDrr3rXEuvO5rNa709A6Ok5vbmU6NTAwOjQ0ODgxOTAwMTo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoxNjo6OjQzODgxOTAwMToxNzc2MzEyMjE4Ojo6MTUxOTcxMTM4MDoyNjc4NDAwOjA6MTlkZWQyYzIwZjJhZDRlMmFmYWZlMzAzMzM1ODNhYjQzOjox"

DETAIL_COOKIE = "ticket=80fdc178173ecb806504deee82ed27f5; user=MDrr3rXEuvO5rNa709A6Ok5vbmU6NTAwOjQ0ODgxOTAwMTo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoxNjo6OjQzODgxOTAwMToxNzc2MzEyMjE4Ojo6MTUxOTcxMTM4MDoyNjc4NDAwOjA6MTlkZWQyYzIwZjJhZDRlMmFmYWZlMzAzMzM1ODNhYjQzOjox"

# ============ 接口地址 ============
# 上升趋势ETF池子接口
POOL_URL = "https://fund.10jqka.com.cn/quotation/fund_pool/v2/query"
# ETF详情指标接口
DETAIL_URL = "https://dataq.10jqka.com.cn/fetch-data-server/fetch/v1/specific_data"
# AI洞察标签接口
AI_INSIGHTS_URL = "https://eq.10jqka.com.cn/open/api/etf_rank/etf/uptrend/v1/ai/insights/tags"


def _pool_headers():
    """获取ETF池子接口的请求头配置"""
    return {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15",
        'Content-Type': "application/json",
        'hexin-v': "A-hg3lGuFXCmUTn0KVen6KGHvdz_EUwbLnUgn6IZNGNW_YfDSiEcq36F8C3x",
        'Origin': "https://fund.10jqka.com.cn",
        'Referer': "https://fund.10jqka.com.cn/thsjj-jj-fe-market-domain/uptrend-list/index.html",
        'Cookie': POOL_COOKIE,
    }


def _detail_headers():
    """获取ETF详情接口的请求头配置"""
    return {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15",
        'Content-Type': "application/json",
        'Origin': "https://fund.10jqka.com.cn",
        'Referer': "https://fund.10jqka.com.cn/",
        'X-Auth-ProgId': "7047",
        'X-Auth-Version': "1.0",
        'Platform': "hxkline",
        'X-Auth-AppName': "AINVEST",
        'X-Auth-Type': "ths",
        'Source-Id': "hxkline-FW_ETFUpTrend_Page",
        'X-Fuyao-Auth': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRob3JpemVyX25hbWVzcGFjZSI6ImNvbW1vbi1ocS1hZ2dyIiwibGljZW5zZWVfdHlwZSI6IkZST05UX0FQUCIsImxpY2Vuc2VlX25hbWVzcGFjZSI6Imh4a2xpbmUtRldfRVRGVXBUcmVuZF9QYWdlIn0.ZSEljLYXljW_vHLvgrAw6F_T2ND8UB4Vktkj7Zs2e-A",
        'Cookie': DETAIL_COOKIE,
    }


def _ai_insights_headers():
    """获取AI洞察标签接口的请求头配置"""
    return {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 hxFont/normal getHXAPPAdaptOldSetting/0 Language/zh-Hans getHXAPPAccessibilityMode/0 hxnoimage/0 getHXAPPFontSetting/normal VASdkVersion/1.2.2 VoiceAssistantVer/0 hxtheme/0 IHexin/11.97.01 (Royal Flush) userid/438819001 innerversion/I037.08.572 build/11.97.02 surveyVer/0 isVip/0",
        'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json",
        'Sec-Fetch-Site': "same-site",
        'sw8': "1-M2VmN2JiZWEtMjBmOC00M2VhLTk4NjktMzE1YjYyYmJkYmEx-ZWMxNmQ2NDQtNGZiZi00MGNhLWIyMjgtNWQ3NmIxYzE1YTI9-0-dGhzamotamotZmVmdW5kLWthbWlzLWh1Yjxicm93c2VyPg==-YmFzaWNfMS4w-Lw==-ZXEuMTBqcWthLmNvbS5jbg==",
        'Accept-Language': "zh-CN,zh-Hans;q=0.9",
        'Sec-Fetch-Mode': "cors",
        'Origin': "https://fund.10jqka.com.cn",
        'Referer': "https://fund.10jqka.com.cn/",
        'Sec-Fetch-Dest': "empty",
    }


def fetch_uptrend_pool():
    """
    接口1: 获取上升趋势ETF列表
    
    Returns:
        list: ETF代码列表，格式为 [(market_code, etf_code), ...]
    """
    payload = {
        "businessKey": "etfUpTrend",  # 业务类型：ETF上升趋势
        "businessPoolKey": "1f3b943f-c5f4-312f-95b9-64de02642115",
        "custom": {"fieldList": ["subMarket"], "limit": 10000, "offset": 0,  "uniqueTracking": False,}
    }
    resp = requests.post(POOL_URL, json=payload, headers=_pool_headers())
    resp.raise_for_status()  # 检查HTTP请求状态
    data = resp.json()

    # 检查接口返回状态码
    if data.get("status_code") != 0:
        raise Exception(f"接口1错误: {data.get('status_msg')}")

    items = data['data']['itemList']
    return items


def fetch_detail(code_list, batch_size=200):
    """
    接口2: 分批获取上升趋势详情指标
    
    Args:
        code_list (list): ETF完整代码列表，格式为 ["market:code", ...]
        batch_size (int): 每批请求的ETF数量，默认200
    
    Returns:
        list: ETF详情数据列表
    """
    all_results = []

    # 分批请求，避免单次请求过多
    for i in range(0, len(code_list), batch_size):
        batch = code_list[i:i + batch_size]
        payload = {
            "code_selectors": {
                "include": [{"type": "stock_code", "values": batch}],
                "exclude": [], "intersection": []
            },
            "indexes": [
                {"index_id": "security_name"},  # 证券名称
                {"index_id": "price_change_ratio_pct", "source_id": "199112", "req_uniq_id": "199112", "needSubscribe": True},  # 当日涨幅
                {"index_id": "etf_up_trend_total_ratio", "needSubscribe": True},  # 趋势总涨幅
                {"index_id": "etf_up_trend_duration"},  # 持续天数
                {"index_id": "etf_up_trend_consecutive_up_days"},  # 连涨天数
                {"index_id": "etf_limit_up_stock_cnt"},  # 涨停股数
                {"index_id": "etf_limit_up_stock_pct"},  # 涨停占比
            ],
            "page_info": {"page_size": len(batch), "page_begin": 0, "code_begin": 0},
            "sort": [{"idx": 1, "type": "desc"}]
        }

        resp = requests.post(DETAIL_URL, json=payload, headers=_detail_headers())
        resp.raise_for_status()
        data = resp.json()

        batch_data = data.get('data', {}).get('data', [])
        all_results.extend(batch_data)

    return all_results


def parse_detail(raw_list):
    """
    解析详情数据，将原始接口数据转换为结构化格式
    
    Args:
        raw_list (list): 原始接口返回的详情数据
    
    Returns:
        list: 解析后的ETF数据列表，每个元素为包含所需字段的字典
    """
    parsed = []
    for item in raw_list:
        # 拆分市场代码和ETF代码
        market, code = item['code'].split(':')
        # 将values数组转换为字典方便访问
        vals = {v['idx']: v['value'] for v in item['values']}

        parsed.append({
            "code": code,  # ETF代码
            "market": "沪市" if market == "20" else "深市",  # 市场：沪市(20)或深市(36)
            "name": vals.get(0, ""),  # ETF名称
            'price_change_ratio_pct': vals.get(1,''),  # 当日涨幅
            "etf_up_trend_total_ratio": vals.get(2,''),  # 趋势总涨幅
            "etf_up_trend_duration": vals.get(3,''),  # 持续天数
            "etf_up_trend_consecutive_up_days": vals.get(4,''),  # 连涨天数
            "etf_limit_up_stock_cnt": vals.get(5,''),  # 涨停股数
            "etf_limit_up_stock_pct": vals.get(6,''),  # 涨停占比
            "full_code": item['code'],  # 完整代码（用于匹配AI标签）
        })
    return parsed


def fetch_ai_insights(code_list):
    """
    接口3: 获取 ETF 上升趋势 AI 洞察标签
    
    Args:
        code_list (list): ETF完整代码列表
    
    Returns:
        dict: 以ETF完整代码为key，标签字符串为value的字典
    """
    payload = {
        "unique_keys": code_list
    }
    
    resp = requests.post(AI_INSIGHTS_URL, json=payload, headers=_ai_insights_headers())
    resp.raise_for_status()
    data = resp.json()
    
    tags_dict = {}
    for item in data.get('data', []):
        # 获取代码，兼容不同的字段名
        code = item.get('code', '') or item.get('unique_key', '')
        tags_list = item.get('tags', [])
        
        # 处理标签列表，转换为逗号分隔的字符串
        if isinstance(tags_list, list):
            tags = ', '.join(tags_list) if tags_list else ''
        else:
            tags = tags_list if tags_list else ''
            
        if code:
            tags_dict[code] = tags
    
    return tags_dict


def merge_tags_to_parsed(parsed, tags_dict):
    """
    将 AI 洞察 tags 合并到 ETF 数据中
    
    Args:
        parsed (list): 解析后的ETF数据列表
        tags_dict (dict): AI标签字典
    
    Returns:
        list: 合并后的ETF数据列表
    """
    for item in parsed:
        # 获取完整代码，如果没有则根据市场类型构造
        full_code = item.get('full_code', f"{item['market'] == '沪市' and '20' or '36'}:{item['code']}")
        item['tags'] = tags_dict.get(full_code, '')  # 添加标签字段
    return parsed


def get_etf_uptrend_data(sort_field=None, sort_order='desc'):
    """
    获取完整的 ETF 上升趋势数据（主入口函数）
    
    执行流程：
    1. 获取上升趋势ETF池子列表
    2. 获取ETF详情指标数据
    3. 解析详情数据
    4. 获取AI洞察标签并合并
    5. 移除临时字段
    6. 按指定字段排序
    
    Args:
        sort_field (str): 排序字段 - 可选值: 
            'price_change_ratio_pct' (当日涨幅), 
            'etf_up_trend_total_ratio' (趋势总涨幅), 
            'etf_up_trend_duration' (持续天数), 
            'etf_up_trend_consecutive_up_days' (连涨天数), 
            'etf_limit_up_stock_cnt' (涨停股数), 
            'etf_limit_up_stock_pct' (涨停占比)
        sort_order (str): 排序顺序 - 'asc' 升序, 'desc' 降序
    
    Returns:
        list: 排序后的ETF数据列表
    """
    
    # Step1: 获取ETF池子列表
    pool_items = fetch_uptrend_pool()

    # Step2: 获取ETF详情指标数据
    code_list = [f"{item[0]}:{item[1]}" for item in pool_items]
    raw = fetch_detail(code_list)

    # Step3: 解析详情数据
    parsed = parse_detail(raw)

    # Step4: 获取 AI 洞察标签并合并
    tags_dict = fetch_ai_insights(code_list)
    parsed = merge_tags_to_parsed(parsed, tags_dict)
    
    # Step5: 移除临时字段 full_code
    for item in parsed:
        item.pop('full_code', None)
    
    # Step6: 排序
    if sort_field:
        # 按指定字段排序
        reverse = sort_order == 'desc'
        parsed = sorted(parsed, key=lambda x: float(x.get(sort_field, 0) or 0), reverse=reverse)
    else:
        # 默认按涨停股占比降序排序
        parsed = sorted(parsed, key=lambda x: float(x['etf_limit_up_stock_pct'] or 0), reverse=True)
    
    return parsed


def get_themes():
    """
    获取主题配置，用于前端筛选ETF
    
    Returns:
        dict: 主题字典，key为主题名称，value为关键词列表
    """
    return {
        "芯片/半导体": ["芯片", "半导体", "集成电路"],
        "人工智能/AI": ["人工智能", "AI"],
        "科创板": ["科创板", "科创50", "科创成长", "科创200"],
        "数字经济": ["数字经济"],
        "有色金属": ["有色金属", "矿业"],
        "新能源": ["新能源", "光伏", "电池", "风电"],
        "消费": ["消费"],
        "医药": ["医药", "医疗"],
        "金融": ["银行", "券商", "金融", "保险"],
        "港股/恒生": ["港股", "恒生", "港交所"],
        "机器人": ["机器人"],
        "军工": ["军工", "国防"],
        "汽车/智驾": ["汽车", "智能驾驶"],
        "红利": ["红利"],
        "黄金": ["黄金"],
        "纳指/标普": ["纳指", "标普"],
    }


if __name__ == "__main__":
    # 测试运行：获取并打印ETF数据
    data = get_etf_uptrend_data()
    print(data)
    print(f"获取到 {len(data)} 条 ETF 数据")
