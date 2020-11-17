# IMPORTS
import pandas as pd
import math
import os.path
import time
from bitmex import bitmex
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
# from tqdm import tqdm_notebook #(Optional, used for progress-bars)
from tqdm import tqdm
import ccxt

### API
bitmex_api_key = 'Y9TSphUiBVfFgJDNk44yBlaK'  # Enter your own API-key here
bitmex_api_secret = '-y1Hgl9KsRZgyWGv31VJRbIlyRa4DsfabbfvK21JbEqbrhcf'  # Enter your own API-secret here

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "30m": 30, "1h": 60, "1d": 1440}
batch_size = 750
bitmex_client = bitmex(test=False, api_key=bitmex_api_key, api_secret=bitmex_api_secret)
binance_client = Client(api_key='Jwn4VgnKwcjSvAmO0VW7XyfnFQShjMxDg3WThuYPxo1pF2UjnCVemy1fnr3C2Teh',
                        api_secret='VlJqt8SZzRBEZMjenIWM0fkR6qWaAagEOMO3Rexz8kgNbZ46PcVqd08OUAVTtZP7')


### FUNCTIONS
# def minutes_of_new_data(symbol, kline_size, data, source):
#     if len(data) > 0:
#         old = parser.parse(data["timestamp"].iloc[-1])
#     elif source == "bitmex":
#         old = \
#             bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=False).result()[
#                 0][0][
#                 'timestamp']
#     if source == "bitmex": new = \
#         bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0][
#             'timestamp']
#     return old, new


def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance":
        old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    elif source == "bitmex":
        old = \
        bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=False).result()[0][0][
            'timestamp']
    if source == "binance": new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0],
                                                 unit='ms')
    if source == "bitmex": new = \
    bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0][
        'timestamp']
    return old, new


def get_all_bitmex(symbol, kline_size, save=False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source="bitmex")
    # oldest_point = datetime.fromisoformat('2017-06-01 00:05:00+00:00')
    delta_min = (newest_point - oldest_point).total_seconds() / 60
    # print (oldest_point, type(oldest_point))
    # print (delta_min)
    available_data = math.ceil(delta_min / binsizes[kline_size])
    rounds = math.ceil(available_data / batch_size)
    if rounds > 0:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data in %d rounds.' % (
            delta_min, symbol, available_data, kline_size, rounds))
        for round_num in tqdm(range(rounds)):
            time.sleep(1)
            new_time = (oldest_point + timedelta(minutes=round_num * batch_size * binsizes[kline_size]))
            data = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=batch_size,
                                                         startTime=new_time).result()[0]
            temp_df = pd.DataFrame(data)
            data_df = data_df.append(temp_df)
    data_df.set_index('timestamp', inplace=True)
    if save and rounds > 0: data_df.to_csv(filename)
    print('All caught up..!')
    return data_df


def get_all_binance(symbol, kline_size, save=False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source="binance")
    delta_min = (newest_point - oldest_point).total_seconds() / 60
    available_data = math.ceil(delta_min / binsizes[kline_size])
    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
        print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
    else:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (
            delta_min, symbol, available_data, kline_size))
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"),
                                                  newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines,
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else:
        data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save: data_df.to_csv(filename)
    print('All caught up..!')
    return data_df


def convert_ohlcv_to_ticker(ohlcv_data):
    """last,buy,sell,mid,timestamp"""
    ticker = []
    for data in ohlcv_data:
        tick = {"last": data[4], "buy": data[4], "sell": data[4], "mid": data[4],
                "timestamp": ccxt.bitmex.iso8601(data[0])}
        ticker.append(tick)
    return ticker


def convert_ohlcv_5m_to_15m(ohlcv5):
    ohlcv15 = []
    # OHLCV key indexes
    timestamp = 0
    open = 1
    high = 2
    low = 3
    close = 4
    volume = 5

    if len(ohlcv5) > 2:
        for i in range(0, len(ohlcv5) - 2, 3):
            highs = [ohlcv5[i + j][high] for j in range(0, 3) if ohlcv5[i + j][high]]
            lows = [ohlcv5[i + j][low] for j in range(0, 3) if ohlcv5[i + j][low]]
            volumes = [ohlcv5[i + j][volume] for j in range(0, 3) if ohlcv5[i + j][volume]]
            candle = [
                ohlcv5[i + 0][timestamp],
                ohlcv5[i + 0][open],
                max(highs) if len(highs) else None,
                min(lows) if len(lows) else None,
                ohlcv5[i + 2][close],
                sum(volumes) if len(volumes) else None,
            ]
            ohlcv15.append(candle)
    else:
        raise Exception('Too few 5m candles')
    return ohlcv15


# get_all_bitmex('XBTUSD', '1m', save = True)


# data_1m_df = pd.read_csv("XBTUSD-1m-data.csv")
# tick_data = []
# for index, row in data_1m_df.iterrows():
#     tick = {"last": row['close'], "buy": row['close'], "sell": row['close'], "mid": row['close'],
#             "timestamp": row['timestamp']}
#     tick_data.append(tick)
# ticker_1m_df = pd.DataFrame(tick_data)
# ticker_1m_df.to_csv("ticker-data-1m.csv")

# get_all_bitmex("LTCUSD", "5m", save=True)
get_all_binance("LTCUSDT", "30m", save=True)
