import configparser
import requests
import wikiquote
from pprint import pprint
from geopy.geocoders import Nominatim
locator = Nominatim(user_agent="Simplex is here.")
config = configparser.ConfigParser()
config.read('config.ini')

static_tags = ['#introvert', '#city', '#love', '#instagood', '#me', '#cute',
               '#tbt', '#photooftheday', '#instamood', '#tweegram',
               '#picoftheday', '#igers', '#beautiful', '#instadaily', '#summer',
               '#instagramhub', '#iphoneonly', '#follow', '#igdaily', '#bestoftheday',
               '#happy', '#picstitch', '#tagblender', '#jj', '#sky', '#fashion',
               '#followme', '#fun', '#sun']


def get_address_tags(city):
    location = None
    try:
        location = locator.geocode(city, language='en')
    except:
        location = locator.geocode(city, language='en')
    return ['#' + i for i in location.address.lower().replace(' ', '').split(',')] if location else []


def form_message(city='new york'):
    quote = f"{wikiquote.quote_of_the_day()[0]} {wikiquote.quote_of_the_day()[1]}"
    message = '.\n'*6
    tags = get_address_tags(city) + static_tags
    message += ''.join(tags[:30])
    pprint(message)
    return message, quote
