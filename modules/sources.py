from bs4 import BeautifulSoup

crap_list = ['coupon', 'contest', 'chance', '.99', 'off', 'buy',
             'spend', 'recipe', 'subscription', 'sweepstakes', 'win',
             'pre-order', 'shipped', 'purchase', 'deal', 'possibl',
             'kroger', 'magazine', 'giveaway', 'ebook', 'ios', 'entrance',
             'cardholder', 'member', 'sale', 'savings', 'as-low',
             'points', 'survey', 'rewards', 'rental', 'starting', 'kmart',
             'Kroger', 'guide', 'only', 'app', 'regular', 'just', '-at-',
             'printable', 'recipe', '_at_', 'download', 'event', 'dvd',
             'dog', 'activity', 'subscription', 'sample', 'video', 'android']

def is_crap(link):
    return any(i.upper() in link.upper() for i in crap_list)

class Sources(object):
    pass


class Hip2Save(Sources):
    urls = ["http://hip2save.com/category/freebies/"]

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for article in soup.findAll("h6",
                                    {"class": "entry-title grid-title "}):
            if len(article.findAll("div",
                                   {"class": "es-flag new-flags"})) == 0:
                link = article.find('a').get('href')
                if link and not is_crap(link):
                    to_send.append(link)
        return to_send


class FreeFlys(Sources):
    child_urls = ['/Free_Samples/Other', '/Free_Samples/Children', '/Free_Samples/Food',
                  '/Free_Samples/Health']
    urls = ['http://www.freeflys.com' + child for child in child_urls]

    @staticmethod
    def process(page):
        links_to_return = []
        soup = BeautifulSoup(page, 'html.parser')
        for topic in soup.findAll("a", {"class": "SO_offerlink"}):
            link = topic.get('href').replace('..', 'http://www.freeflys.com')
            if link and not is_crap(link):
                links_to_return.append(link)
        return links_to_return


class Reddit(Sources):
    urls = ['https://www.reddit.com/r/freebies/']

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for topic in soup.findAll("p", {"class": "title"}):
            link = topic.find('a').get('href')
            if link.startswith('/r'):
                continue
            if link and not is_crap(link):
                to_send.append(link)
        return to_send


class Hunt4Freebies(Sources):
    urls = ['http://hunt4freebies.com/']

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for topic in soup.findAll("h2", {"class": "entry-title"}):
            link = topic.find('a').get('href')
            if link and not is_crap(link):
                to_send.append(link)
        return to_send


class CouponProBlog(Sources):
    urls = ['http://www.couponproblog.com/category/freebies/']

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for post in soup.findAll("div", {"class": "headline_area"}):
            if len(post.findAll("div", {"class": "expired_imghead"})) == 0:
                link = str(post.find('a')).split('href="')[-1].split('"', 1)[0]
                if link and not is_crap(link):
                    to_send.append(link)
        return to_send
