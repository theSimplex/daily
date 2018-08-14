import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import datetime
import time
from PIL import Image
import os

def plot_stuff():
    with open('data.csv') as file:
        reader = csv.reader(file)
        data = [i for i in reader]
    data = data[::-1]
    stocks_data_full = [json.loads(i[1].replace("'", '"')) for i in data]
    crypto_data_full = [json.loads(i[0].replace("'", '"')) for i in data]
    time_data = [datetime.datetime.fromtimestamp(int(float(i[-1]))) for i in data]
    stocks_total_cost = [i.get('total_value') for i in stocks_data_full]
    crypto_total_cost = [sum([j['cash_value'] for j in i]) for i in crypto_data_full]
    data_filtered = []
    date = None
    for record in zip(time_data, stocks_total_cost, crypto_total_cost):
        if record[0].day == date:
            continune
        else:
            data_filtered.append(record)
    dates, stocks, cryptos = zip(*data_filtered)
    bg_color = 'black'
    fg_color = 'white'
    fig = plt.figure(facecolor=bg_color, edgecolor=fg_color)
    axes = fig.add_subplot(111)
    axes.patch.set_facecolor(bg_color)
    axes.xaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
    axes.yaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
    for spine in axes.spines.values():
        spine.set_color(fg_color)
    plt.plot(dates, stocks, color='yellow', label='Stocks')
    plt.plot(dates, cryptos, color='cyan', label='Crypto')
    plt.plot(dates, [sum(x) for x in zip(stocks, cryptos)], color='white', label='Total')
    legend = plt.legend(frameon = 1)
    frame = legend.get_frame()
    frame.set_edgecolor('white')
    frame.set_facecolor('grey')
    plt.xlabel('Time flying by')
    plt.ylabel('Money $$$')
    timestamp_ = int(time.time())
    fig.autofmt_xdate()
    plt.savefig(f'graphs/{timestamp_}_plot.png', facecolor = fig.get_facecolor(), transparent = True)
    Image.open(f'graphs/{timestamp_}_plot.png').convert('RGB').save(f'graphs/{timestamp_}_plot.jpg','JPEG')
    for file in os.listdir('graphs/'):
        if file != f'{timestamp_}_plot.jpg':
            os.remove(f'graphs/{file}')
    return timestamp_

plot_stuff()