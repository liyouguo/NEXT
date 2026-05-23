import pywencai

try:
    # 查询沪深300成分股 - 获取完整数据
   
    hs300 = pywencai.get(
        question="今年涨幅top20,场外基金", 
        query_type="fund",
        per_page=100,  # 每页100条
        loop=True      # 循环获取所有页
    )
    # print(f"\n获取到{len(hs300)}条沪深300成分股数据:")
    print(hs300)  # 打印前10条
    
    # # 查询贵州茅台完整信息
    # print("\n正在获取贵州茅台完整数据...")
    # maotai = pywencai.get(
    #     question="贵州茅台 市值 市盈率 ROE", 
    #     query_type="stock",
    #     per_page=50,
    #     loop=True
    # )
    # print("\n贵州茅台完整信息:")
    # print(maotai)

except Exception as e:
    print(f"\n发生错误: {str(e)}")
    print("请检查网络连接或API限制")
