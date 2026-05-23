"""
Flask 服务器主文件
负责路由和API接口，数据获取由独立模块处理
主要功能：
1. 提供前端页面路由
2. 提供各个功能的API接口
3. 处理数据请求和响应
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sys
import os

# 添加当前目录到路径，确保模块导入正常
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入独立的数据模块
from data import get_nasdaq_chart_data, get_etf_uptrend_data, get_themes, get_fund_signal_data, get_fund_pool, get_batch_fund_signals, get_fund_pool_data, get_preset_queries, get_broad_index_data

# 初始化Flask应用
app = Flask(__name__, static_folder='.')
# 启用CORS，允许跨域请求
CORS(app)


# ============ 页面路由 ============
@app.route('/')
@app.route('/index.html')
def index():
    """首页 - 导航页面"""
    return send_from_directory('.', 'index.html')


@app.route('/nasdaq.html')
def nasdaq_page():
    """NASDAQ 指数页面"""
    return send_from_directory('static', 'nasdaq.html')


@app.route('/etf.html')
def etf_page():
    """ETF 上升趋势页面"""
    return send_from_directory('static', 'etf.html')


@app.route('/fund')
@app.route('/fund.html')
def fund_page():
    """基金波动分析页面"""
    return send_from_directory('.', 'fund.html')


@app.route('/fund_pool')
@app.route('/fund_pool.html')
def fund_pool_page():
    """基金池筛选页面"""
    return send_from_directory('.', 'fund_pool.html')


@app.route('/broad_index')
@app.route('/broad_index.html')
def broad_index_page():
    """宽基指数趋势页面"""
    return send_from_directory('.', 'broad_index.html')


# ============ NASDAQ API ============
@app.route('/api/nasdaq/data', methods=['GET'])
def get_nasdaq_data():
    """
    获取 NASDAQ 指数数据
    
    Returns:
        JSON: 包含成功状态和数据的响应
    """
    try:
        data = get_nasdaq_chart_data()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/nasdaq/refresh', methods=['POST'])
def refresh_nasdaq_data():
    """
    刷新 NASDAQ 指数数据
    
    Returns:
        JSON: 包含成功状态和刷新结果的响应
    """
    try:
        data = get_nasdaq_chart_data()
        return jsonify({
            'success': True,
            'count': len(data),
            'date_range': f"{data[0]['PDATE']} ~ {data[-1]['PDATE']}" if data else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ ETF API ============
@app.route('/api/etf/data', methods=['GET'])
def get_etf_data():
    """
    获取 ETF 上升趋势数据
    
    Query参数:
        sortField (str): 排序字段，可选
        sortOrder (str): 排序顺序，可选，默认desc
    
    Returns:
        JSON: 包含成功状态、ETF数据和主题配置的响应
    """
    try:
        # 获取查询参数
        sort_field = request.args.get('sortField')
        sort_order = request.args.get('sortOrder', 'desc')
        
        # 获取数据
        data = get_etf_uptrend_data(sort_field=sort_field, sort_order=sort_order)
        themes = get_themes()
        
        return jsonify({
            'success': True,
            'data': data,
            'themes': themes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/etf/refresh', methods=['POST'])
def refresh_etf_data():
    """
    刷新 ETF 上升趋势数据
    
    Body参数:
        sortField (str): 排序字段，可选
        sortOrder (str): 排序顺序，可选，默认desc
    
    Returns:
        JSON: 包含成功状态、数据条数和数据的响应
    """
    try:
        # 获取请求体参数
        data = request.get_json() or {}
        sort_field = data.get('sortField')
        sort_order = data.get('sortOrder', 'desc')
        
        # 刷新并获取数据
        etf_data = get_etf_uptrend_data(sort_field=sort_field, sort_order=sort_order)
        
        return jsonify({
            'success': True,
            'count': len(etf_data),
            'data': etf_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ 基金 API ============
@app.route('/api/fund/data', methods=['GET'])
def get_fund_data():
    """
    获取基金波动分析数据
    
    Query参数:
        code (str): 基金代码，可选，默认015790
        timeRange (str): 时间范围，可选，默认Month
    
    Returns:
        JSON: 包含成功状态和数据的响应
    """
    try:
        code = request.args.get('code', '015790')
        time_range = request.args.get('timeRange', 'Month')
        data = get_fund_signal_data(code=code, time_range=time_range)
        
        if 'error' in data:
            return jsonify({
                'success': False,
                'error': data['error'],
                'errorCode': data.get('errorCode', -1)
            }), 400
            
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fund/refresh', methods=['POST'])
def refresh_fund_data():
    """
    刷新基金波动分析数据
    
    Body参数:
        code (str): 基金代码，可选，默认015790
        timeRange (str): 时间范围，可选，默认Month
    
    Returns:
        JSON: 包含成功状态和数据的响应
    """
    try:
        data = request.get_json() or {}
        code = data.get('code', '015790')
        time_range = data.get('timeRange', 'Month')
        fund_data = get_fund_signal_data(code=code, time_range=time_range)
        
        if 'error' in fund_data:
            return jsonify({
                'success': False,
                'error': fund_data['error'],
                'errorCode': fund_data.get('errorCode', -1)
            }), 400
            
        return jsonify({
            'success': True,
            'data': fund_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fund/pool', methods=['GET'])
def get_fund_pool_api():
    """
    获取预设基金池列表
    
    Returns:
        JSON: 包含成功状态和基金池列表的响应
    """
    try:
        fund_pool = get_fund_pool()
        return jsonify({
            'success': True,
            'data': fund_pool
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fund/batch', methods=['GET', 'POST'])
def get_batch_fund_data():
    """
    批量查询基金数据
    
    Query参数 (GET) / Body参数 (POST):
        fundCodes: 基金代码列表，可选，不传则使用默认基金池
        timeRange: 时间范围，可选，默认Month
    
    Returns:
        JSON: 包含成功状态和所有基金数据的响应
    """
    try:
        fund_codes = None
        time_range = 'Month'
        
        if request.method == 'POST':
            data = request.get_json() or {}
            fund_codes = data.get('fundCodes')
            time_range = data.get('timeRange', 'Month')
        else:
            time_range = request.args.get('timeRange', 'Month')
            # 从query参数获取基金代码列表（用逗号分隔）
            codes_param = request.args.get('fundCodes')
            if codes_param:
                fund_codes = [code.strip() for code in codes_param.split(',') if code.strip()]
        
        batch_data = get_batch_fund_signals(fund_codes=fund_codes, time_range=time_range)
        
        return jsonify({
            'success': True,
            'data': batch_data,
            'count': len(batch_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ 基金池 API ============
@app.route('/api/fund_pool/presets', methods=['GET'])
def get_fund_pool_presets():
    """
    获取基金池预设查询条件
    
    Returns:
        JSON: 包含成功状态和预设条件的响应
    """
    try:
        presets = get_preset_queries()
        return jsonify({
            'success': True,
            'presets': presets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fund_pool/data', methods=['GET', 'POST'])
def get_fund_pool_data_api():
    """
    获取基金池数据
    
    参数:
        question (str): 查询问题，可通过GET query或POST body传递
    
    Returns:
        JSON: 包含成功状态和基金池数据的响应
    """
    try:
        question = None
        if request.method == 'POST':
            data = request.get_json() or {}
            question = data.get('question')
        else:
            question = request.args.get('question')
        
        fund_pool_data = get_fund_pool_data(question=question)
        
        if not fund_pool_data.get('success'):
            return jsonify(fund_pool_data), 400
        
        return jsonify(fund_pool_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ 宽基指数 API ============
@app.route('/api/broad_index/data', methods=['GET'])
def get_broad_index():
    """
    获取宽基指数趋势数据
    
    Returns:
        JSON: 包含宽基指数数据的响应
    """
    try:
        data = get_broad_index_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/broad_index/refresh', methods=['POST'])
def refresh_broad_index():
    """
    刷新宽基指数数据
    
    Returns:
        JSON: 包含宽基指数数据的响应
    """
    try:
        data = get_broad_index_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    """
    启动Flask应用
    监听0.0.0.0:5000端口，支持调试模式
    """
    print("=" * 50)
    print("🚀 美股性价比分析系统启动中...")
    print("=" * 50)
    print("📊 首页: http://localhost:5000")
    print("📈 NASDAQ: http://localhost:5000/nasdaq.html")
    print("💎 ETF: http://localhost:5000/etf.html")
    print("💰 基金: http://localhost:5000/fund")
    print("🎯 基金池: http://localhost:5000/fund_pool")
    print("📉 宽基指数: http://localhost:5000/broad_index")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
