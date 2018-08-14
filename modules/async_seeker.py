import asyncio
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

from modules.async_crawler import AsyncCrawler
from modules.clients.telegrammer import Telegrammer

headers = {'User-Agent':
           ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')}


class Seeker(Telegrammer):
    def __init__(self):
        self.sent = []
        with open('log.dat', 'r') as f:
            sent_links = [i.strip('\n') for i in f.readlines()]
            for old_link in sent_links:
                if old_link[-1] == '/':
                    old_link = old_link[:-1]
                self.sent.append(old_link)
            self.sent_tails = [i.split('/')[-1] for i in self.sent]
        with open('config.json') as config_file:
            self.config = json.loads(config_file.read())
        self.message_url = "https://api.telegram.org/bot{}/".format(
            self.config['telegram_token'])
        self.chat = self.config['chat_id']
        self.heartbeat = self.config['heartbeat_id']
        self.goodies_list = self.config['good_stuff']
        self.loop = asyncio.get_event_loop()

    def process_stuff(self, links):
        self.loop.run_until_complete(self.link_processor(links))

    async def link_processor(self, links):
        ignored = 0
        saved, bird_food = [], []
        for link in links:
            if link[-1] == '/':
                link = link[:-1]
            if link in self.sent:
                ignored += 1
                continue
            elif link.split('/')[-1] in self.sent_tails:
                print('Found duplicate: {}'.format(link))
            else:
                self.send_text(link)
                if any(key in link for key in self.goodies_list):
                    self.send_heartbeat(link)
                bird_food.append(link)
                saved.append(link)
        with open('log.dat', 'w') as f:
            if len(self.sent) > 2000:
                self.sent = self.sent[-2000:]
            for link_ in self.sent + links:
                f.write(link_ + '\n')
        self.put_new_tweets_for_the_bird(bird_food)
        print('Ignored {} links as previously sent.'.format(ignored))

    def put_new_tweets_for_the_bird(self, urls):
        with open('new.dat', 'w') as f:
            for link_ in urls:
                f.write(link_ + '\n')


def seek():
    while True:
        try:
            timeout = 900
            ds = Seeker()
            crawler = AsyncCrawler()
            start = time.time()
            freebies = crawler.crawl()
            stop = time.time() - start
            print('Found {} links in {}s.'.format(len(freebies), stop))
            ds.process_stuff(freebies)
            total_stop = time.time() - start
            print('Did full cycle in {}s. Going to sleep for {}s'.format(
                total_stop, timeout))
            time.sleep(timeout)
        except KeyboardInterrupt:
            raise
        except:
            print('Failure: ', sys.exc_info()[0])
