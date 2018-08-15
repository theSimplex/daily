import os
from modules.async_seeker import seek
from multiprocessing import Process
from aiotg import Bot, Chat
from modules.hashtag import form_message
from modules.stock_market import summary_scheduler
from modules.crypto import crypto_scheduler
import configparser


config = configparser.ConfigParser()
config.read('config.ini')


def botsman():
    bot = Bot(api_token=config.get('Telegram', 'token'))

    @bot.command(r"/hash (.+)")
    def hashtag(chat: Chat, match):
        message, quote = form_message(match.group(1))
        chat.send_text(f'{quote}\n {message}')
        chat.send_text(f'<>\n {message}')
    bot.run()

if __name__ == '__main__':
    processes = []
    processes.append(Process(target=summary_scheduler, args=()))
    processes.append(Process(target=crypto_scheduler, args=()))
    processes.append(Process(target=seek, args=()))
    processes.append(Process(target=botsman, args=()))
    print(f"Press Ctrl+{'Break' if os.name == 'nt' else 'C'} to exit")
    try:
        for p in processes:
            p.start()
    except (KeyboardInterrupt, SystemExit):
        for p in processes:
            p.join()
