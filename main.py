
import investpy
import pandas as pd
import datetime
import dateutil
import matplotlib.pyplot as plt

# basic_data = investpy.commodities.get_commodity_historical_data(commodity='Gold', from_date='01/01/1900',
#                                                                 to_date='01/02/2022')
# basic_data.to_csv('gold_data.csv') #创建原始数据表格


def data_update():
    exist_date = pd.read_csv('gold_data.csv', parse_dates=['Date'], index_col=['Date']) #读取原始表格
    last_date = pd.read_csv('gold_data.csv', parse_dates=['Date']).iloc[-1, 0] #读取原始表格中最新日期
    from_date = last_date.strftime("%d/%m/%Y") #确定起始日期
    today = datetime.date.today() #获取今日日期
    to_date = today.strftime("%d/%m/%Y") #确定结束日期
    delta_data = investpy.commodities.get_commodity_historical_data(commodity='Gold', from_date=from_date,
                                                                    to_date=to_date).iloc[1:, :] #获取并切片上次更新后至最新日期的数据
    updated_data = exist_date.append(delta_data) #将新数据加致原数据后
    updated_data.to_csv('gold_data.csv') #生成最新数据csv


CASH = 100000
START_DATE = '2021-01-30'
END_DATE = '2022-02-08'


class General_info: #通用变量对象，给initialize, handle_data函数使用
    pass


general_info = General_info()


class Context: #初始现金，起始日期，结束日期，基准，考虑交易日的起止日期，时间
    def __init__(self, cash, start_date, end_date):
        self.cash = cash
        self.start_date = start_date
        self.end_date = end_date
        self.positions = {}
        self.benchmark = None
        trade_cal = pd.read_csv('gold_data.csv')
        self.date_range = trade_cal[(trade_cal['Date'] >= start_date) & \
                                    (trade_cal['Date'] <= end_date)]['Date'].values
        self.dt = None #计算时当前日期


context = Context(CASH, START_DATE, END_DATE)
trade_cal = pd.read_csv('gold_data.csv')


def set_benchmark(commodity):
    context.benchmark = commodity


def attribute_daterange_history(commodity, start_date, end_date, fields=('Open', 'Close', 'High', 'Low', 'Volume')):
    df = pd.read_csv(commodity + '.csv', index_col='Date', parse_dates=['Date']).loc[start_date:end_date, :]
    return df[list(fields)]


def attribute_history(commodity, count, fields=('Open', 'Close', 'High', 'Low', 'Volume')):
    end_date = (context.dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = trade_cal[trade_cal['Date'] <= end_date][-count:].iloc[0, 0] #从上至下，对应日期从远到近，同‘gold_data.csv’顺序
    return attribute_daterange_history(commodity, start_date, end_date, fields)


def get_today_data(commodity):
    today = context.dt.strftime('%Y-%m-%d')
    data = pd.read_csv(commodity + '.csv', index_col='Date', parse_dates=['Date']).loc[today, :]
    return data


def _order(today_data, commodity, amount):
    price = today_data['Open'].squeeze()
    if len(today_data) == 0:
        print("今日停牌")
        return

    if context.cash - amount * price < 0:
        amount = int(context.cash / price)
        print("现金不足,已调整为%d" % amount)

    if context.positions.get(commodity, 0) < -amount:
        amount = -context.positions.get(commodity, 0)
        print("超过现有持仓，已调整为%d" % amount)

    context.positions[commodity] = context.positions.get(commodity, 0) + amount #更新仓位信息

    context.cash -= amount * price #更新资金信息

    if context.positions[commodity] == 0:
        del context.positions[commodity]


def order(commodity, amount):
    today_data = get_today_data(commodity)
    _order(today_data, commodity, amount)


def order_target(commodity, amount):
    if amount < 0:
        print("数量不能为负，已调整为0")
        amount = 0

    today_data = get_today_data(commodity)
    hold_amount = context.positions.get(commodity, 0)
    delta_amount = amount - hold_amount
    _order(today_data, commodity, delta_amount)


def order_value(commodity, value):
    today_data = get_today_data(commodity)
    amount = int(value / today_data['Open'].squeeze())
    _order(today_data, commodity, amount)


def order_target_value(commodity, value):
    today_data = get_today_data(commodity)
    if value < 0:
        print("价值不能为负，已调整为0")
        value = 0

    hold_value = context.positions.get(commodity, 0) * today_data['Open'].squeeze()
    delta_value = (value - hold_value)
    order_value(commodity, delta_value)


# ---------------------------------------AREA TO BE MODIFIED FOR EACH STRATEGY------------------------------------------
def initialize(context):
    set_benchmark('gold_data')
    general_info.p1 = 5
    general_info.p2 = 60
    general_info.commodity = 'gold_data'


def handle_data(context):
    hist = attribute_history(general_info.commodity, general_info.p2) #从上至下，对应日期从近到远，同‘gold_data.csv’顺序
    ma5 = hist['Close'][:general_info.p1].mean()
    ma60 = hist['Close'][:general_info.p2].mean()

    if ma5 > ma60 and general_info.commodity not in context.positions:
        order_value(general_info.commodity, context.cash)
        print('trade date:' + str(context.dt))
        print('cash:' + str(context.cash))
        print('positions:' + str(context.positions))
        print('------------------')
    elif ma5 < ma60 and general_info.commodity in context.positions:
        order_target(general_info.commodity, 0)
        print('trade date:' + str(context.dt))
        print('cash:' + str(context.cash))
        print('positions:' + str(context.positions))
        print('------------------')
# ---------------------------------------AREA TO BE MODIFIED FOR EACH STRATEGY (END)------------------------------------


def run():
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range), columns=['value'])
    init_value = context.cash
    initialize(context)
    last_price = {}
    for dt in context.date_range:
        context.dt = dateutil.parser.parse(dt)
        handle_data(context)
        current_value = context.cash
        for commodity in context.positions:
            today_data = get_today_data(commodity)
            if len(today_data) == 0:
                price = last_price[commodity]
            else:
                price = today_data['Open'].squeeze()
                last_price[commodity] = price
            current_value += price * context.positions[commodity]
        plt_df.loc[dt, 'current_value'] = current_value
    plt_df['strategy_earning_ratio'] = (plt_df['current_value'] - init_value) / init_value #计算策略收益率

    bm_df = attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    bm_init = bm_df['Open'][-1]
    plt_df['benchmark_earning_ratio'] = (bm_df['Open'] - bm_init) / bm_init #计算基准收益率
    plt_df[['strategy_earning_ratio', 'benchmark_earning_ratio']].plot()
    plt.show()



run()