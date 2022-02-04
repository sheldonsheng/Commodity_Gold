import time

import investpy
import pandas as pd
import datetime

def data_update():
    f = open('gold_data.csv', 'r')
    exist_data = pd.read_csv(f, parse_dates=['Date'], index_col=['Date'])
    f = open('gold_data.csv', 'r')
    last_date = pd.read_csv(f, parse_dates=['Date']).iloc[-1, 0]
    from_date = last_date.strftime("%d/%m/%Y")
    today = datetime.date.today()
    to_date = today.strftime("%d/%m/%Y")
    time_mark = today.strftime('%Y-%m-%d')
    delta_data = investpy.commodities.get_commodity_historical_data(commodity='Gold', from_date=from_date, to_date=to_date)\
        .iloc[1:, :]
    updated_data = exist_data.append(delta_data)
    print(updated_data)
    updated_data.to_csv('gold_data_updated_date:' + time_mark + '.csv')


#test


