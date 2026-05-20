"""
Flask 服务器主文件
负责路由和API接口，数据获取由独立模块处理
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# 添加当前目录到路径，确保模块导入正常
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入独立的数据模块
from data import get_nasdaq_chart_data, get_etf_uptrend_data, get_themes

app = Flask(__name__, static_folder='static')
CORS(app)


# ============ 页面路由 ============
@app.route('/')
def index():
    """首页 - 导航页面"""
    return send_from_directory('static', 'index.html')


@app.route('/nasdaq')
def nasdaq_page():
    """NASDAQ 指数页面"""
    return send_from_directory('static', 'nasdaq.html')


@app.route('/etf')
def etf_page():
    """ETF 上升趋势页面"""
    return send_from_directory('static', 'etf.html')


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
        data = get_etf_uptrend_data()
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
        data = get_etf_uptrend_data()
        return jsonify({
            'success': True,
            'count': len(data)
        })
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
    print("� NASDAQ: http://localhost:5000/nasdaq")
    print("💎 ETF: http://localhost:5000/etf")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
