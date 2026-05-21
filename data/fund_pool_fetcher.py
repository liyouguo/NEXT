"""
基金池数据获取模块
使用问财API获取基金筛选条件
"""
import pywencai
import pandas as pd
from datetime import datetime


def get_fund_pool_data(question=None, query_type="fund", per_page=100, loop=True):
    """
    获取基金池数据
    
    Args:
        question: 问财查询语句，默认：今年涨幅top20,场外基金
        query_type: 查询类型，默认 fund
        per_page: 每页数量
        loop: 是否循环获取所有页
    
    Returns:
        字典格式的基金池数据
    """
    if question is None:
        question = "今年涨幅top20,场外基金"
    
    try:
        print(f"正在查询问财：{question}")
        df = pywencai.get(
            question=question,
            query_type=query_type,
            per_page=per_page,
            loop=loop
        )
        
        if df is None or len(df) == 0:
            return {
                "success": False,
                "error": "未获取到数据"
            }
        
        # 处理数据格式化
        result = {
            "success": True,
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "count": len(df),
            "funds": []
        }
        
        # 转换DataFrame为字典列表
        df = df.reset_index()
        for idx, row in df.iterrows():
            fund_info = {}
            for col in df.columns:
                val = row[col]
                # 处理NaN值
                if pd.isna(val):
                    val = ""
                elif isinstance(val, (int, float)):
                    # 数值类型保持原样
                    pass
                fund_info[col] = val
            
            result["funds"].append(fund_info)
        
        return result
        
    except Exception as e:
        print(f"问财查询错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_preset_queries():
    """
    获取预设的查询条件列表
    
    Returns:
        预设查询列表
    """
    return [
        {
            "id": "top_gain",
            "name": "今年涨幅TOP20",
            "question": "今年涨幅top20,场外基金",
            "description": "今年以来涨幅最大的20只场外基金"
        },
        {
            "id": "high_profit",
            "name": "高收益",
            "question": "近一年收益率>50%,场外基金",
            "description": "近一年收益率超过50%的基金"
        },
        {
            "id": "low_risk",
            "name": "低风险",
            "question": "近一年波动率<10%,近一年夏普比率>1,场外基金",
            "description": "低波动且风险调整后收益高的基金"
        },
        {
            "id": "tech_theme",
            "name": "科技主题",
            "question": "科技主题,近一年收益率>30%,场外基金",
            "description": "科技主题基金，近一年收益>30%"
        },
        {
            "id": "consumption_theme",
            "name": "消费主题",
            "question": "消费主题,近一年收益率>30%,场外基金",
            "description": "消费主题基金，近一年收益>30%"
        },
        {
            "id": "custom",
            "name": "自定义",
            "question": "",
            "description": "自定义查询条件",
            "is_custom": True
        }
    ]


if __name__ == '__main__':
    # 测试
    print("测试获取基金池...")
    data = get_fund_pool_data()
    print(data)
