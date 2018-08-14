import configparser
from datetime import datetime
from binance.client import Client
from binance import exceptions
from clients.telegrammer import Telegrammer

config = configparser.ConfigParser()
config.read('config.ini')
bi = Client(config.get('Binance', 'api_key'), config.get('Binance', 'secret_key'))
t = Telegrammer(token=config.get('Telegram', 'token'),
                chat_id=config.get('Telegram', 'chat_id'),
                heartbeat_id=config.get('Telegram', 'heartbeat_id'))


def get_balances():
    account = bi.get_account()
    assets = []
    for asset in account['balances']:
        if float(asset['free']) > 0:
            asset['price'], change = get_symbol_price(asset['asset']) 
            assets.append({**asset, **change})
    return calculate_cash_value(assets)

def get_symbol_price(symbol='BTC'):
    if symbol == 'BTC':
        change = get_24hr_price_change('BTCUSDT')
        return 'N/A', change
    try:
        price = bi.get_symbol_ticker(symbol=symbol+'BTC')['price']
        change = get_24hr_price_change(symbol+'BTC')
        return price, change
    except exceptions.BinanceAPIException:
        print(f'failed to get price for {symbol+pair}')

def get_24hr_price_change(symbol):
    change = bi.get_historical_klines(symbol=symbol, 
                                      interval=bi.KLINE_INTERVAL_1DAY, 
                                      start_str=datetime.now().strftime("%B %d, %Y"))
    open_price = float(change[0][1])
    close_price = float(change[0][4])
    return {'daily_actual_change': close_price - open_price,
            'daily_percentage_change': (close_price - open_price)/open_price*100}

def calculate_cash_value(assets):
    btc_price = float(bi.get_symbol_ticker(symbol='BTCUSDT')['price'])
    assets_to_return = []
    for asset in assets:
        if asset['asset'] == 'BTC':
            asset['price'] = btc_price
            asset['cash_value'] = float(asset['free']) * btc_price
            assets_to_return.append(asset)
        else:
            asset['btc_value'] = float(asset['free']) * float(asset['price'])
            asset['cash_value'] = asset['btc_value'] * btc_price
            if asset['cash_value'] > 1.0:
                trades = bi.get_my_trades(symbol=f"{asset['asset']}BTC")
                if trades:
                    asset['base_cost'] = float(asset['free']) * float(trades[-1]['price']) * btc_price
                else:
                    asset['base_cost'] = float(asset['free']) * float(bi.get_historical_klines(symbol=f"{asset['asset']}BTC", interval='1d', start_str='1 month ago')[-1][1]) * btc_price
                assets_to_return.append(asset)
    return assets_to_return

def form_message(assets):
    message = '🌇 Crypto summary:\n'
    for asset in assets:
        message += f"{asset['asset']} {round(asset['cash_value'], 2)}$ ({round(asset['daily_percentage_change'], 2)}%{get_emoji(asset['daily_percentage_change'])})\n"
    was_total_value = round(sum([i['cash_value']*100/(100 + i['daily_percentage_change']) for i in assets]), 2)
    total_value = round(sum([i['cash_value'] for i in assets]), 2)
    total_percentage_change = total_value/was_total_value*100 - 100
    message += f"🕰️ Total: {total_value}$ ({round(total_percentage_change, 2)}%{get_emoji(total_percentage_change)})"
    return message

def get_emoji(percentage):
    return '🔻' if percentage < 0 else '💹'

def get_daily_summary_crypto(q=None):
    result = get_balances()
    if q:
        q.put({'crypto': result})
    else:
        t.send_text(form_message(result))

if __name__=='__main__':
    get_daily_summary_crypto()