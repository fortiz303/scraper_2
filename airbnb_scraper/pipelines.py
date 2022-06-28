# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

import requests
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


def telegram_message(item):
    """ Send Message to telegram"""
    item_data =[f'{k}: {v}' for k, v in item.items()]
    message = "\n".join(item_data)
    params = {
        'chat_id': os.environ['scraper_airbnb_chat_id'],
        'text': message
    }
    try:
        API_URL = f'https://api.telegram.org/bot{os.environ["scraper_airbnb_telegram_token"]}/sendMessage'
        response = requests.post(API_URL, params=params)

    except:
        pass


file_path = os.path.join(os.getcwd(), f'tracker/track_id.txt')


def write_seen(host_id):
    """ Write the Home ID scraped"""
    with open(file_path, 'a+') as f:
        f.write(str(host_id) + '\n')


def read_seen() -> set:
    """ Read saved Home IDs """
    return set(line.strip() for line in open(file_path, 'r'))


class AirbnbScraperPipeline(object):
    def __init__(self):
        self.seen = set()

    def open_spider(self, spider):

        self.seen = read_seen()

    def process_item(self, item, spider):
        """ Remove duplicate items"""

        adapter = ItemAdapter(item)
        host_id = adapter['host_id']

        if host_id in self.seen:
            raise DropItem(f'Duplicate Item found {host_id}')
        else:
            self.seen.add(host_id)
            write_seen(host_id)
            telegram_message(item)
            return item
