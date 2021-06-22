import redis
import requests
import time
import datetime
import logging
import pprint
import bs4

logging.basicConfig(level=logging.DEBUG)

def refresh_currencies():
    resp = requests.get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
    document = bs4.BeautifulSoup(resp.text, features='lxml-xml')
    date = None
    currencies = dict()
    for item in document.findChild('Cube').findChildren():
        if isinstance(item, str): continue
        if item.get('time'):
            date = item.get('time')
        if item.get('currency') and item.get('rate'):
            currencies[ item.get('currency') ] = item.get('rate')
    
    print('Got currencies:')
    pprint.pprint(currencies)
    print('Connecting to Redis and storing currencies...')
    
    db = redis.Redis(host='redis_currency')
    pipe = db.pipeline()
    pipe.flushdb()
    pipe.set('date', date)
    for curr in currencies:
        pipe.set(curr, currencies[curr])
    print('Redis response:', pipe.execute())


while True:
    print('Performing refresh now...')
    refresh_currencies()
    dt = datetime.datetime.now()
    until_next_hour = (datetime.datetime.min - dt) % datetime.timedelta(hours=1)
    print('Refresh complete, waiting', until_next_hour, 'until the top of next hour')
    time.sleep(until_next_hour.total_seconds())
