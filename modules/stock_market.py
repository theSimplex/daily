import configparser
import csv
from multiprocessing import Queue
from time import time

from clients.robinhood import Robinhood
from clients.telegrammer import Telegrammer
from weekly import plot_stuff
from datetime import datetime
from pprint import pprint

config = configparser.ConfigParser()
config.read('config.ini')
rh = Robinhood(username=config.get('User', 'username'),
               password=config.get('User', 'password'))
t = Telegrammer(token=config.get('Telegram', 'token'),
                chat_id=config.get('Telegram', 'chat_id'),
                heartbeat_id=config.get('Telegram', 'heartbeat_id'))


def get_current_positions_summary():
    profits = {}
    all_positions = rh.positions()
    existing_positions = [position for position in all_positions['results']
                          if float(position['quantity']) > 0.0]
    for position in existing_positions:
        instrument_id = position['instrument'].split('/')[-2]
        instrument = rh.instrument(instrument_id)
        quote = rh.quote_data(instrument['symbol'])
        base_cost = float(position['average_buy_price']) * float(position['quantity'])
        current_value = float(quote['bid_price']) * float(position['quantity'])
        previous_day_value = float(quote['adjusted_previous_close']) * float(position['quantity'])
        total_profit = round(current_value - base_cost, 2)
        daily_profit = round(current_value - previous_day_value, 2)
        total_percentage = round(total_profit/base_cost * 100, 2)
        daily_percentage = round(daily_profit/base_cost * 100, 2)
        profits[quote['symbol']] = {'value': current_value,
                                    'total_profit': total_profit,
                                    'daily_profit': daily_profit,
                                    'total_%': total_percentage,
                                    'daily_%': daily_percentage}
    print(f"Fetched data for: {', '.join([i for i in profits])}")
    summary = {'profits': profits}
    summary['daily_total_profit'] = sum([profits[i]['daily_profit'] for i in profits])
    summary['total_current_value'] = sum([profits[i]['value'] for i in profits])
    summary['daily_total_%'] = round(summary['daily_total_profit']/summary['total_current_value'] * 100, 2)
    return summary


def get_balance():
    account_info = rh.get_account()
    return float(account_info['margin_balances']['unallocated_margin_cash'])


def total_profit():
    total_transfer = 0.0
    for transfer in rh.transfers().get('results'):
        total_transfer += float(transfer['amount'])
    market_value = float(rh.portfolios().get('market_value'))
    return market_value - total_transfer


def get_string_message(summary):
    message = f"🏦 *Stock summary*:\n"
    for symbol in sorted(summary['profits'].items(), key=lambda x: x[1]['total_profit'], reverse=True):
        line = ''
        line += f"*{symbol[0]}:"
        line += f"  {round(symbol[1]['value'], 2)}$ *"
        line += f"   ({get_emoji(symbol[1]['daily_%'])} "
        line += f"_{symbol[1]['total_profit']}$_).\n"
        message += line
    message += f"\n_Daily profit: {summary['daily_total_profit']} {get_emoji(summary['daily_total_%'])}_"
    message += f"\nTotal profit: *{round(total_profit(), 2)}$*"
    message += f"\n*🐲Total stocks: {round(summary['total_current_value'], 2)}$*"
    return message


def get_emoji(percentage):
    return '🔻' if percentage < 0 else '💹'


def get_summary():
    summary = get_current_positions_summary()
    summary['money'] = get_balance()
    summary['diff'] = total_profit()
    message = get_string_message(summary)
    t.send_text(message, formatted=True)


def summary_scheduler():
    while True:
        if date.today().weekday() > 4 and datetime.now().hour in [8, 15]:
            get_summary()
            time.sleep(3601)
            

get_summary()