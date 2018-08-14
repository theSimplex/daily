import configparser
import csv
from multiprocessing import Queue
from time import time

from clients.robinhood import Robinhood
from clients.telegrammer import Telegrammer
from crypto import get_daily_summary_crypto
from weekly import plot_stuff
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')
rh = Robinhood(username=config.get('User', 'username'),
               password=config.get('User', 'password'))
t = Telegrammer(token=config.get('Telegram', 'token'),
                chat_id=config.get('Telegram', 'chat_id'),
                heartbeat_id=config.get('Telegram', 'heartbeat_id'))


def get_current_positions():
    full_info = []
    all_positions = rh.positions()
    existing_positions = [position for position in all_positions['results']
                          if float(position['quantity']) > 0.0]
    for position in existing_positions:
        instrument_id = position['instrument'].split('/')[-2]
        instrument = rh.instrument(instrument_id)
        quote = rh.quote_data(instrument['symbol'])
        full_info.append({**position, **instrument, **quote})
    print(f"Fetched data for: {', '.join([i['symbol'] for i in full_info])}")
    return full_info


def get_balance():
    account_info = rh.get_account()
    return float(account_info['margin_balances']['unallocated_margin_cash'])


def total_profit():
    total_transfer = 0.0
    for transfer in rh.transfers().get('results'):
        total_transfer += float(transfer['amount'])
    market_value = float(rh.portfolios().get('market_value'))
    return market_value - total_transfer


def summarize_profits(q):
    cash_on_hands = get_balance()
    positions_summary = get_current_positions()
    profits = {}
    for position in positions_summary:
        if float(position['average_buy_price']) == 0.0:
            position['average_buy_price'] = '0.01'
        profits[position['symbol']] = calculate_position_profit(position)
    profit_summary = {'symbols': profits}
    profit_summary['total_profit'] = round(
        sum([i['total_profit'] for i in profits.values()]), 2)
    profit_summary['daily_profit'] = round(
        sum([i['daily_profit'] for i in profits.values()]), 2)
    profit_summary['total_cost'] = sum(
        [i['base_cost'] for i in profits.values()])
    profit_summary['total_value'] = sum(
        [i['current_value'] for i in profits.values()]) + cash_on_hands
    profit_summary['daily_profit_percentage'] = round(
        profit_summary['daily_profit']/profit_summary['total_cost']*100, 2)
    profit_summary['total_profit_percentage'] = round(
        profit_summary['total_profit']/profit_summary['total_cost']*100, 2)
    result = {**profit_summary, **find_best_performer(profits)}
    if q:
        q.put({'stock': result})
    return result


def get_daily_summary(plot=False):
    q = Queue()
    # get_daily_summary_crypto(q)
    if rh.auth:
        summarize_profits(q)
    message = form_message(q)
    t.send_text(message, formatted=True)
    if plot:
        send_plot()


def send_plot():
    photo = open(f'graphs/{plot_stuff()}_plot.jpg', 'rb')
    t.send_image(photo=photo)


def form_message(q):
    summary = {**q.get(), **q.get()}
    summary['timestamp'] = time()
    message = f"🏦 *Stock summary*:\n"
    for symbol in sorted(summary['stock']['symbols'].items(), key=lambda x: x[1]['current_value'], reverse=True):
        line = ''
        line += f"*{symbol[0]}:"
        line += f"  {round(symbol[1]['current_value'], 2)}$ *"
        line += f"   ({get_emoji(symbol[1]['daily_profit_percentage'])} "
        line += f"_{symbol[1]['total_profit']}$_).\n"
        message += line
    message += f"""\n_Daily profit: {summary['stock']['daily_profit']}$ ({summary['stock']['daily_profit_percentage']}% {get_emoji(summary['stock']['daily_profit_percentage'])})_
Total profit: *{round(total_profit(), 2)}$*
🐲Total stocks: *{round(summary['stock']['total_value'], 2)}$*
=========================
🌇 *Crypto summary*:
"""
    for asset in sorted(summary['crypto'], key=lambda x: x['cash_value'], reverse=True):
        message += f"*{asset['asset']}: {round(asset['cash_value'], 2)}$ *"
        message += f"({get_emoji(asset['daily_percentage_change'])}"
        if asset.get('base_cost'):
            message += f" _{round(asset['cash_value'] - asset['base_cost'], 2)}$_"
        message += ')\n'
    was_total_value = round(sum(
        [i['cash_value']*100/(100 + i['daily_percentage_change']) for i in summary['crypto']]), 2)
    total_value = round(sum([i['cash_value'] for i in summary['crypto']]), 2)
    total_percentage_change = total_value/was_total_value*100 - 100
    message += "\n"
    message += f"🕰️ Total crypto: *{total_value}$* ({round(total_percentage_change, 2)}%{get_emoji(total_percentage_change)})\n"
    message += "=========================\n"
    message += f"n\🚀 *Total: {round(summary['stock']['total_value'] + total_value, 2)}$* 🚀"
    try:
        save_summary_to_file(summary)
    except Exception as e:
        print(f'Failed to log results. {e}')
    return message


def save_summary_to_file(summary):
    file = 'data.csv'
    with open(file, 'a') as f:
        w = csv.DictWriter(f, summary.keys())
        w.writerow(summary)


def get_emoji(percentage):
    return '🔻' if percentage < 0 else '💹'


def find_best_performer(profits):
    default_symbol = list(profits.keys())[0]
    hero = default_symbol
    best_percentage = profits[hero]['daily_profit_percentage']
    loser = hero
    worst_percentage = best_percentage
    for symbol in profits:
        if profits[symbol]['daily_profit_percentage'] > best_percentage:
            hero = symbol
            best_percentage = profits[symbol]['daily_profit_percentage']
        elif profits[symbol]['daily_profit_percentage'] < worst_percentage:
            loser = symbol
            worst_percentage = profits[symbol]['daily_profit_percentage']
    performers = {
        'Best': f"{hero} {best_percentage}% ({profits[hero]['daily_profit']}$ {get_emoji(best_percentage)})",
        'Worst': f"{loser} {worst_percentage}% ({profits[loser]['daily_profit']}$ {get_emoji(worst_percentage)})"
    }
    return performers


def calculate_position_profit(position):
    profit = {}
    profit['base_cost'] = float(
        position['quantity']) * float(position['average_buy_price'])
    profit['current_value'] = float(
        position['quantity']) * float(position['last_trade_price'])
    profit['total_profit'] = round(
        profit['current_value'] - profit['base_cost'], 2)
    profit['total_profit_percentage'] = round(
        profit['total_profit']/profit['base_cost'] * 100, 2)
    profit['daily_profit'] = round(
        float(position['last_trade_price']) - float(position['previous_close']), 2)
    profit['daily_profit_percentage'] = round(
        profit['daily_profit']/float(position['previous_close']) * 100, 2)
    return profit


if __name__ == '__main__':
    get_daily_summary()
