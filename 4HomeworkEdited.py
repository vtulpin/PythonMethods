from pprint import pprint
from lxml import html
import requests
import re
from pymongo import MongoClient

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/85.0.4183.102 Safari/537.36'}
main_link = 'https://lenta.ru'

response = requests.get(main_link, headers=header)
main_dom = html.fromstring(response.text)

news_blocks = main_dom.xpath("//div[@class='b-yellow-box__wrap']//div[@class='item']")

lenta_news = []

for block in news_blocks:
    lenta_news_dict = {}
    title = block.xpath(".//text()")[0]
    link = block.xpath(".//@href")[0]

    if link[0] == '/':
        full_link = main_link + link
        get_date = re.findall(r'(\d{4})/(\d{2})/(\d{2})', link)[0]
        source = 'Lenta.ru'
        lenta_news_dict['date'] = f'{get_date[0]}-{get_date[1]}-{get_date[2]}'
    else:
        full_link = link
        get_date = re.findall(r"(\d{2})-(\d{2})-(\d{4})", link)[0]
        source = re.findall(r"https://(\w+.ru)", link)[0]
        lenta_news_dict['date'] = f'{get_date[2]}-{get_date[1]}-{get_date[0]}'

    lenta_news_dict['title'] = title.replace('\xa0', ' ')
    lenta_news_dict['link'] = full_link
    lenta_news_dict['source'] = source
    lenta_news.append(lenta_news_dict)

client = MongoClient('127.0.0.1', 27017)
db = client['news_db']
news = db.news
news.insert_many(lenta_news)

pprint(lenta_news)
