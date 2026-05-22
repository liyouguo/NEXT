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
        question = "今年涨幅top20,近一年波动率,近三年波动率,场外基金"
    
    try:
        print(f"正在查询问财：{question}")
        df = pywencai.get(
            question=question,
            query_type=query_type,
            per_page=per_page,
            loop=loop
        )
        
        if df is None or len(df) == 0:
            # 尝试简化查询，去掉波动率条件
            print("未获取到数据，尝试简化查询...")
            simple_question = "今年涨幅top20,场外基金"
            df = pywencai.get(
                question=simple_question,
                query_type=query_type,
                per_page=per_page,
                loop=loop
            )
            
            if df is None or len(df) == 0:
                return {
                    "success": False,
                    "error": "未获取到数据，尝试简化查询也失败"
                }
            question = simple_question
        
        print(f"成功获取到 {len(df)} 行数据，{len(df.columns)} 列")
        
        # 处理数据格式化
        result = {
            "success": True,
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "count": len(df),
            "columns": list(df.columns),
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
            
            # 添加波动风险评估
            fund_info = add_risk_analysis(fund_info)
            result["funds"].append(fund_info)
        
        print(f"数据处理完成，共 {len(result['funds'])} 只基金")
        return result
        
    except Exception as e:
        print(f"问财查询错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }


def add_risk_analysis(fund_info):
    """
    为基金添加风险分析信息
    
    Args:
        fund_info: 基金信息字典
    
    Returns:
        添加了风险分析的基金信息
    """
    # 尝试获取近一年波动率
    volatility = None
    volatility_col = None
    
    # 寻找包含波动率的列名（处理问财返回的列名格式）
    for col in fund_info.keys():
        if "波动率" in col:
            # 优先选择包含"一年"的列
            if "一年" in col:
                volatility_col = col
                val = fund_info[col]
                if isinstance(val, (int, float)):
                    volatility = val
                elif isinstance(val, str):
                    try:
                        # 尝试从字符串中提取数值（处理百分比格式）
                        cleaned = val.replace('%', '').replace(',', '')
                        volatility = float(cleaned)
                    except:
                        pass
                break
    
    # 如果没找到带"一年"的，找任意波动率列
    if volatility is None:
        for col in fund_info.keys():
            if "波动率" in col:
                volatility_col = col
                val = fund_info[col]
                if isinstance(val, (int, float)):
                    volatility = val
                elif isinstance(val, str):
                    try:
                        cleaned = val.replace('%', '').replace(',', '')
                        volatility = float(cleaned)
                    except:
                        pass
                break
    
    # 再尝试找"年化波动率"
    if volatility is None:
        for col in fund_info.keys():
            if "年化波动率" in col:
                volatility_col = col
                val = fund_info[col]
                if isinstance(val, (int, float)):
                    volatility = val
                elif isinstance(val, str):
                    try:
                        cleaned = val.replace('%', '').replace(',', '')
                        volatility = float(cleaned)
                    except:
                        pass
                break
    
    if volatility is not None:
        # 波动率风险评级
        if volatility < 10:
            risk_level = "低"
            risk_tag = "🟢 低风险"
        elif volatility < 20:
            risk_level = "中"
            risk_tag = "🟡 中风险"
        elif volatility < 30:
            risk_level = "较高"
            risk_tag = "🟠 较高风险"
        else:
            risk_level = "高"
            risk_tag = "🔴 高风险"
        
        fund_info["波动率数值"] = volatility
        fund_info["风险评级"] = risk_level
        fund_info["风险标签"] = risk_tag
        if volatility_col:
            fund_info["波动率来源"] = volatility_col
    else:
        # 如果没有找到波动率，添加说明
        fund_info["风险标签"] = "⚪ 数据不足"
        fund_info["风险评级"] = "未知"
    
    return fund_info


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
            "question": "今年涨幅top20,近一年波动率,场外基金",
            "description": "今年以来涨幅最大的20只场外基金，包含波动率数据"
        },
        {
            "id": "yearly_return_top20",
            "name": "近一年收益TOP20",
            "question": "近一年收益率top20,近一年波动率,场外基金",
            "description": "近一年收益率最高的20只基金，包含波动率数据"
        },
        {
            "id": "high_profit",
            "name": "高收益",
            "question": "近一年收益率>30%,近一年波动率,场外基金",
            "description": "近一年收益率超过30%的基金，包含波动率数据"
        },
        {
            "id": "low_risk",
            "name": "低风险",
            "question": "近一年波动率<15%,近一年夏普比率>1,近一年波动率,场外基金",
            "description": "低波动且风险调整后收益高的基金，包含波动率数据"
        },
        {
            "id": "tech_theme",
            "name": "科技主题",
            "question": "科技主题,近一年收益率,近一年波动率,场外基金",
            "description": "科技主题基金，包含收益率和波动率数据"
        },
        {
            "id": "consumption_theme",
            "name": "消费主题",
            "question": "消费主题,近一年收益率,近一年波动率,场外基金",
            "description": "消费主题基金，包含收益率和波动率数据"
        },
        {
            "id": "volatility_ranking",
            "name": "波动率排行",
            "question": "近一年波动率,近一年收益率,场外基金",
            "description": "按近一年波动率排行，帮助评估风险"
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
