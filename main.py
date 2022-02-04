import investpy
import pandas as pd
import datetime

basic_data = investpy.commodities.get_commodity_historical_data(commodity='Gold', from_date='01/01/1900',
                                                                to_date='01/02/2022')
basic_data.to_csv('gold_data.csv') #创建原始数据表格


def data_update():
    f = open('gold_data.csv', 'r')
    exist_data = pd.read_csv(f, parse_dates=['Date'], index_col=['Date']) #读取原始表格
    f = open('gold_data.csv', 'r')
    last_date = pd.read_csv(f, parse_dates=['Date']).iloc[-1, 0] #读取原始表格中最新日期
    from_date = last_date.strftime("%d/%m/%Y") #确定起始日期
    today = datetime.date.today() #获取今日日期
    to_date = today.strftime("%d/%m/%Y") #确定结束日期
    time_mark = today.strftime('%Y-%m-%d') #转化为中国习惯格式日期，文件名备用
    delta_data = investpy.commodities.get_commodity_historical_data(commodity='Gold', from_date=from_date,
                                                                    to_date=to_date).iloc[1:, :] #获取并切片上次更新后至最新日期的数据
    updated_data = exist_data.append(delta_data) #将新数据加致原数据后
    print(updated_data)
    updated_data.to_csv('gold_data_updated_date:' + time_mark + '.csv') #生成最新数据csv


data_update()
# test
