# 📊 美股性价比分析系统

专业的美股指数与ETF投资分析工具，提供实时数据可视化和投资机会挖掘。

## ✨ 功能特性

### 📈 纳斯达克指数分析
- 实时跟踪纳斯达克综合指数
- 收盘价与信号评分双轴图表
- 关键统计指标展示
- 自动刷新数据

### 💎 ETF上升趋势挖掘
- 实时获取处于上升趋势的ETF列表
- 趋势总涨幅、持续天数、连涨天数等详细指标
- AI洞察标签
- 主题分类筛选（芯片、AI、科创板等）
- 涨停股占比排序

## 🏗️ 项目结构

```
美股性价比/
├── data/                           # 数据模块（独立可维护）
│   ├── __init__.py
│   ├── etf_fetcher.py             # ETF数据获取模块
│   └── nasdaq_fetcher.py          # NASDAQ数据获取模块
├── static/                         # 前端静态文件
│   ├── index.html                 # 首页导航
│   ├── nasdaq.html                # NASDAQ分析页面
│   └── etf.html                   # ETF分析页面
├── server.py                       # Flask后端服务
├── requirements.txt                # Python依赖
└── README.md                       # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python server.py
```

### 3. 访问应用

打开浏览器访问：
- 🏠 **首页**: http://localhost:5000
- 📈 **纳斯达克指数**: http://localhost:5000/nasdaq
- 💎 **ETF上升趋势**: http://localhost:5000/etf

## 📡 API 接口

### NASDAQ 相关

#### 获取数据
```
GET /api/nasdaq/data
```

#### 刷新数据
```
POST /api/nasdaq/refresh
```

### ETF 相关

#### 获取数据
```
GET /api/etf/data
```

#### 刷新数据
```
POST /api/etf/refresh
```

## 🛠️ 技术栈

- **后端**: Flask + Python
- **前端**: HTML5 + CSS3 + Chart.js
- **数据来源**: 天天基金API
- **架构设计**: 模块化，前后端分离

## 📝 配置说明

### ETF Cookie 配置

由于同花顺API需要登录认证，当Cookie过期时，需要更新 `data/etf_fetcher.py` 中的Cookie配置：

```python
POOL_COOKIE = "your_new_cookie_here"
DETAIL_COOKIE = "your_new_cookie_here"
```

获取Cookie的方法：
1. 打开浏览器开发者工具（F12）
2. 访问同花顺相关页面
3. 在Network标签页中找到请求
4. 复制Request Headers中的Cookie值

## 🎨 界面预览

### 首页
- 深色主题设计
- 卡片式导航
- 功能特性介绍

### NASDAQ页面
- 统计卡片展示
- 可切换图表
- 实时数据更新

### ETF页面
- 主题筛选按钮
- 摘要统计
- 数据表格展示
- 标签化AI洞察

## 🔄 数据刷新

- 页面自动每5分钟刷新数据
- 支持手动点击刷新按钮
- 显示最后更新时间

## 📦 依赖说明

- `flask`: Web框架
- `flask-cors`: 跨域支持
- `requests`: HTTP请求库

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
