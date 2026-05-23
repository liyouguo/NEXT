"""
Flask 服务器主文件
负责路由和API接口，数据获取由独立模块处理
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sys
import os

# 添加当前目录到路径，确保模块导入正常
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入独立的数据模块
from data import get_nasdaq_chart_data, get_etf_uptrend_data, get_themes, get_fund_signal_data, get_fund_pool_data, get_preset_queries, get_broad_index_data

app = Flask(__name__, static_folder='.')
CORS(app)


# ============ 页面路由 ============
@app.route('/')
@app.route('/index.html')
def index():
    """首页 - 导航页面"""
    return send_from_directory('.', 'index.html')


@app.route('/nasdaq.html')
# @app.route('/nasdaq.html')
def nasdaq_page():
    """NASDAQ 指数页面"""
    return send_from_directory('static', 'nasdaq.html')


@app.route('/etf.html')
# @app.route('/etf.html')
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
    """
    try:
        sort_field = request.args.get('sortField')
        sort_order = request.args.get('sortOrder', 'desc')
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
    """
    try:
        data = request.get_json() or {}
        sort_field = data.get('sortField')
        sort_order = data.get('sortOrder', 'desc')
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
    """
    try:
        from flask import request
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


# ============ 基金池 API ============
@app.route('/api/fund_pool/presets', methods=['GET'])
def get_fund_pool_presets():
    """
    获取基金池预设查询条件
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
def get_fund_pool():
    """
    获取基金池数据
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
    print("=" * 50)
    print("🚀 美股性价比分析系统启动中...")
    print("=" * 50)
    print("📊 首页: http://localhost:5000")
    print("📈 NASDAQ: http://localhost:5000/nasdaq")
    print("💎 ETF: http://localhost:5000/etf")
    print("💰 基金: http://localhost:5000/fund")
    print("🎯 基金池: http://localhost:5000/fund_pool")
    print("📉 宽基指数: http://localhost:5000/broad_index")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
