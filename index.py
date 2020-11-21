from flask import Flask, request, jsonify, abort
import pandas as pd
import talib
import random

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/api/v1.0/backtest', methods=['POST'])
def create_task():
    data_df = pd.read_csv("data/LTCUSDT-30m-data.csv")
    if not request.json or not 'params' in request.json:
        abort(400)
    params = request.json['params']
    order_history_df = run_strategy(data_df, params)
    result = {'performanceReport': {'profit': 0, 'max_dd': 0, 'max_ru': 0,
                                    'num_win': 0, 'num_loss': 0,
                                    'total_win_profit': 0,
                                    'total_loss_profit': 0,
                                    'ave_win': 0, 'ave_loss': 0,
                                    'win_rate': 0, 'balance': 0,
                                    'startBalance': 0,
                                    'relativeYearlyProfit': 0, 'market': 0,
                                    'sharpe': 0,
                                    'trades': 0}}

    if order_history_df.shape[0] != 0:
        report = performance_report(order_history_df)
        print(report)
        result = {
            'performanceReport': {'profit': report['profit'], 'max_dd': report['max_dd'], 'max_ru': report['max_ru'],
                                  'num_win': report['num_win'], 'num_loss': report['num_loss'],
                                  'total_win_profit': report['total_win_profit'],
                                  'total_loss_profit': report['total_loss_profit'],
                                  'ave_win': report['ave_win'], 'ave_loss': report['ave_loss'],
                                  'win_rate': report['win_rate'], 'balance': report['balance'],
                                  'startBalance': report['startBalance'],
                                  'relativeYearlyProfit': report['relativeYearlyProfit'], 'market': report['market'],
                                  'sharpe': report['sharpe'],
                                  'trades': report['trades']}}

    return jsonify(result), 200


def run_strategy(data, params):
    # calculating
    rsi_bull = talib.RSI(data['close'], timeperiod=params['RSI_BULL'])
    rsi_bear = talib.RSI(data['close'], timeperiod=params['RSI_BEAR'])
    sma_slow = talib.SMA(data['close'], timeperiod=params['SML_SLOW'])
    sma_fast = talib.SMA(data['close'], timeperiod=params['SMA_FAST'])
    adx = talib.ADX(high=data['high'], low=data['low'], close=data['close'], timeperiod=params['ADX'])

    order_history = []
    entry_price = 0
    exit_price = 0
    dd = 0
    ru = 0
    dd_percent = 0
    ru_percent = 0

    sma_timeframe = params['SMA_TF']
    adx_timeframe = params['ADX_TF']
    rsi_bull_timeframe = params['RSI_BULL_TF']
    rsi_bear_timeframe = params['RSI_BEAR_TF']
    rsi_bull_high = params['RSI_BULL_HIGH']
    rsi_bull_low = params['RSI_BULL_LOW']
    rsi_bear_high = params['RSI_BEAR_HIGH']
    rsi_bear_low = params['RSI_BEAR_LOW']
    adx_high = params['ADX_HIGH']
    adx_low = params['ADX_LOW']
    bull_mod_high = params['BULL_MOD_HIGH']
    bull_mod_low = params['BULL_MOD_LOW']
    bear_mod_high = params['BEAR_MOD_HIGH']
    bear_mod_low = params['BEAR_MOD_LOW']
    stop_loss = params['STOP_LOSS']  # %
    take_profit = params['TAKE_PROFIT']  # %

    sma_slow_count = 0
    sma_fast_count = 0
    adx_count = 0
    rsi_bull_count = 0
    rsi_bear_count = 0

    in_position = False
    in_fake_position = False  # position if dont have stop loss/take profit
    sma_fast_value = 0
    sma_slow_value = 0
    adx_value = 0

    for index, row in data.iterrows():
        price = row['close']
        # SMA slow
        if sma_slow_count >= sma_timeframe:
            sma_slow_value = sma_slow[index]
            sma_slow_count = 0
        else:
            sma_slow_count += 1

        # SMA fast
        if sma_fast_count >= sma_timeframe:
            sma_fast_value = sma_fast[index]
            sma_fast_count = 0
        else:
            sma_fast_count += 1

        # ADX
        if adx_count >= adx_timeframe:
            adx_value = adx[index]
            adx_count = 0
        else:
            adx_count += 1

        # RSI bull
        rsi_bull_value = rsi_bull[index]

        # RSI bear
        rsi_bear_value = rsi_bear[index]

        is_bull_market = sma_fast_value > sma_slow_value
        is_bear_market = sma_fast_value < sma_slow_value

        # dd, ru
        if in_position:
            dd = min(dd, price)
            dd_percent = 100 * (dd / price - 1)
            ru = max(ru, price)
            ru_percent = 100 * (ru / price - 1)
            # stop/take profit
            if (1 - price / entry_price) > stop_loss / 100 or (price / entry_price - 1) > take_profit / 100:
                # print("Sell at: ", price)
                # print("------------")
                exit_price = price
                # save history
                order_history.append(
                    {"entry": entry_price, "exit": exit_price, "profit": 100 * (exit_price / entry_price - 1),
                     "draw_down": dd, "run_up": ru, "draw_down_percent": dd_percent, "run_up_percent": ru_percent})
                in_position = False
        else:
            dd = 0
            ru = 0
            dd_percent = 0
            ru_percent = 0

        if is_bull_market:
            if adx_value > adx_high:
                rsi_bull_high_adx = rsi_bull_high + bull_mod_high
            elif adx_value < adx_low:
                rsi_bull_low_adx = rsi_bull_low + bull_mod_low
            if not in_position and rsi_bull_value >= rsi_bull_high:
                # print("------------")
                # print("Buy at: ", price)
                in_position = True
                entry_price = price
                dd = ru = price
            elif in_position and rsi_bull_value <= rsi_bull_low:
                # print("Sell at: ", price)
                # print("------------")
                exit_price = price
                # save history
                order_history.append(
                    {"entry": entry_price, "exit": exit_price, "profit": 100 * (exit_price / entry_price - 1),
                     "draw_down": dd, "run_up": ru, "draw_down_percent": dd_percent, "run_up_percent": ru_percent})
                in_position = False

        elif is_bear_market:
            if adx_value > adx_high:
                rsi_bear_high_adx = rsi_bear_high + bear_mod_high
            elif adx_value < adx_low:
                rsi_bear_low_adx = rsi_bear_low + bear_mod_low
            if not in_position and rsi_bear_value >= rsi_bear_high:
                # print("------------")
                # print("Buy at: ", price)
                in_position = True
                entry_price = price
                dd = ru = price
            elif in_position and rsi_bear_value <= rsi_bear_low:
                # print("Sell at: ", price)
                # print("------------")
                exit_price = price
                order_history.append(
                    {"entry": entry_price, "exit": exit_price, "profit": 100 * (exit_price / entry_price - 1),
                     "draw_down": dd, "run_up": ru, "draw_down_percent": dd_percent, "run_up_percent": ru_percent})
                in_position = False
    return pd.DataFrame(order_history)


def performance_report(order_df):
    total_profit = order_df['profit'].sum()
    max_dd = order_df['draw_down_percent'].min()
    max_ru = order_df['run_up_percent'].max()
    num_win = order_df[order_df.profit >= 0].count().profit
    num_loss = order_df[order_df.profit < 0].count().profit
    total_win_profit = order_df[order_df.profit >= 0].sum().profit
    total_loss_profit = order_df[order_df.profit < 0].sum().profit
    ave_win = total_win_profit / num_win
    ave_loss = total_loss_profit / num_loss
    win_rate = num_win / (num_win + num_loss)
    start_price = order_df.iloc[0]['entry']
    end_price = order_df.iloc[-1]['exit']
    market = (end_price / start_price - 1) * 100
    start_balance = 100
    balance = start_balance * (1 + total_profit / 100)
    relative_profit = balance - start_balance
    relative_yearly_profit = relative_profit / 3
    sharpe = 10
    trades = order_df.shape[0] * 2

    return {'profit': float(total_profit), 'max_dd': float(max_dd), 'max_ru': float(max_ru),
            'num_win': int(num_win), 'num_loss': int(num_loss),
            'total_win_profit': int(total_win_profit),
            'total_loss_profit': int(total_loss_profit),
            'ave_win': float(ave_win), 'ave_loss': float(ave_loss),
            'win_rate': float(win_rate), 'balance': float(balance), 'startBalance': float(start_balance),
            'relativeYearlyProfit': float(relative_yearly_profit), 'market': float(market), 'sharpe': float(sharpe),
            'trades': int(trades), 'startPrice': float(start_price), 'endPrice': float(end_price),
            'relativeProfit': float(relative_profit)}


if __name__ == '__main__':
    app.run()
