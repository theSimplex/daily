import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from modules.sources import Sources

headers = {'User-Agent':
           ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')}


class AsyncCrawler(object):

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.links = []

    async def get_links(self, sources):
        async with ClientSession() as session:
            for source in sources:
                for url in source.urls:
                    async with session.get(url, headers=headers) as response:
                        response = await response.read()
                        self.links.append(source.process(response))

    def crawl(self):
        self.loop.run_until_complete(self.get_links(Sources.__subclasses__()))
        return list({item for sublist in self.links for item in sublist})