from datetime import datetime
import time
from dateutil.relativedelta import *
import subprocess


def run():
    date_range = {"from_date": "2018-01-01 00:00", "to_date": "2019-01-01 00:00"}
    config_file = open('config/config-btc-usdt-rsi-bull-bear-adx-stop-loss-short-sample.js', 'r')
    config = config_file.read()
    start_date = datetime.strptime(date_range['from_date'], '%Y-%m-%d %H:%M')
    end_date = datetime.strptime(date_range['to_date'], '%Y-%m-%d %H:%M')
    for i in range (1, 12):
        print("Start round ", i)
        from_date = start_date + relativedelta(months=+i, days=-1)
        from_date_str = datetime.strftime(from_date, '%Y-%m-%d 19:20')
        to_date = start_date + relativedelta(months=+(1+i))
        to_date_str = datetime.strftime(to_date, '%Y-%m-%d 00:00')
        new_config_file_name = 'config/config-btc-usdt-rsi-bull-bear-adx-stop-loss-short-{year}-{month}-{date}.js'.format(year=from_date.year,
                                                            month= from_date.month, date = from_date.day)
        new_config_file = open(new_config_file_name, 'w')
        new_config_file.write(config.replace("#FROM_DATE#", from_date_str).replace("#TO_DATE#", to_date_str))
        new_config_file.close()

        # find best GA config
        # check all node process before run
        p0 = subprocess.Popen("ps -e|grep node", shell=True)
        out0, err0 = p0.communicate()
        print(out0)
        p = subprocess.Popen("node run.js -c {}".format(new_config_file_name), shell=True)
        p1 = subprocess.Popen("ps -e|grep node", shell=True)
        out1, err1 = p1.communicate()
        print(out1)
        time.sleep(2)
        # p.terminate()
        # p.kill()
        break
    config_file.close()
run()