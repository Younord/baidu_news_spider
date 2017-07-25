# -*- coding: utf-8 -*-
import scrapy
import json
import time
import sched
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from baidu.send_email import send_ms
import urllib.parse
from scrapy import Request
from baidu.items import BaiduItem, BaiduLoader
from scrapy_dupefilter_util import DUPEFILTER_PIPELINE_CONFIG, REQUEST_DUPEFILTER_CONFIG


class BaidunewsSpider(scrapy.Spider):
    name = 'baiduNews'
    allowed_domains = ['news.baidu.com']
    item = {'item': BaiduItem, 'collection': 'hzds_brands_article'}
    custom_settings = {
        'ITEM_PIPELINES': {
            # "baidu.pipelines.BaiduPipeline": 500,
            # "baidu.pipelines.DropItemPipeline": 100,
            "scrapy_dupefilter_util.DupefilterPipeline": 300,
            # "scrapy.redis.pipelines.RedisPipeline": 500,
        },
        # 'LOG_FILE': 'scrapy.log',  # 将日志信息存储到文件中
        # 'LOG_LEVEL': 'ERROR',
        'DUPEFILTER_DEBUG': True,
        # 'DOWNLOAD_DELAY': 0.25,
        # 'MONGO_URI': '127.0.0.1:27017',  # 本地
        # 'MONGO_DATABASE': 'baidu',
        # 'ELASTICSEARCH_SERVER': ['10.214.208.166:9200', '10.214.208.167:9200', '10.214.208.168:9200'],

        'MONGO_URI': '10.214.224.142:20000',
        'MONGO_DATABASE': 'crawler-baidunews',
        'DUPEFILTER_CLASS': "scrapy_dupefilter_util.ItemRequestDupeFilter",
        DUPEFILTER_PIPELINE_CONFIG: {'items': [{'item': BaiduItem, 'collection': 'hzds_brands_article'}]},
        REQUEST_DUPEFILTER_CONFIG: {'items': [{'item': BaiduItem, 'collection': 'hzds_brands_article'}]},
    }

    def get_brands(self, separator):
        import pymongo
        con = pymongo.MongoClient("10.214.224.142", 20000)
        db = con['hzds']
        collection = db['hzds_store']
        brand_list = []
        for obj in collection.find({}):
            if obj['store_name'] != obj['store_name_en']:
                brand_list.append(obj['store_name'] + separator + obj['store_name_en'])
            else:
                brand_list.append(obj['store_name'])
        print(brand_list)
        return brand_list

    def start_requests(self):
        # words = self.get_brands()
        # words = ["香奈儿 Chanel", "迪奥 Dior", "HERMES 爱马仕", "Coach 寇驰", "Furla 芙拉",
        #          "Prada 普拉达", "FENDI 芬迪", "倩碧 CLINIQUE", "SK-II", "玉兰油 OLAY",
        #          "兰芝 LANEIGE", "雪花秀 Sulwhasoo", "MCM", "纪梵希 Givenchy", "珑镶 LONGCHAMP",
        #          ]
        words = self.get_brands(',')
        # words = ['奥迪,Audi']
        # words = ['迪奥']
        for word in words:
            # for ct in 0, 1:
            search_word = word.replace(',', ' ')
            params = {'word': search_word, 'pn': 0, 'rn': 20, 'ct': 0}  # ct=0(时间排序)ct=1(焦点排序)
            url = 'https://news.baidu.com/news?tn=bdapinewsearch&' + urllib.parse.urlencode(params)
            yield Request(url=url, meta={'params': params, 'keywords': word}, callback=self.parse_search)

    def parse_search(self, response):
        import hashlib
        params = response.meta.get('params')
        keywords = response.meta.get('keywords')
        timestamp = json.loads(response.body_as_unicode())['timestamp']
        json_res = json.loads(response.body_as_unicode())['data']
        for news in json_res.get('list'):
            item = BaiduLoader(item=BaiduItem())
            if timestamp - news.get('publicTime') > 7*24*3600:
                return None
            item.add_value('post_time',
                           time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(float(news.get('publicTime')))))
            item.add_value('search_word', params.get('word'))
            item.add_value('author', news.get('author'))
            item.add_value('title', news.get('title'))
            item.add_value('link', news.get('url'))
            item.add_value('hash_id', hashlib.md5(news.get('url').encode('utf8')).hexdigest())
            item.add_value('cover_urls', news.get('imgUrl'))  # cover image url
            intro = item.load_item()
            new_url = 'https://news.baidu.com/news?tn=bdapiinstantfulltext&src=' + news.get('url')

            if keywords is None:
                print('error')
                print(news.get('url'))
            yield Request(url=new_url,
                          meta={'intro': intro,
                                'enter_url': news.get('url'),
                                'keywords': response.meta.get('keywords').split(','),
                                },
                          callback=self.parse)
        total = json_res.get('total')
        is_continue = len(json_res.get('list')) == params['rn'] and params['pn'] < total
        if is_continue:
            params['pn'] = params['pn'] + params['rn']
            url = "http://m.news.baidu.com/news?tn=bdapinewsearch&" + urllib.parse.urlencode(params)
            yield scrapy.Request(url=url,
                                 meta={'params': params, 'keywords': keywords},
                                 callback=self.parse_search)

    def parse(self, response):
        import datetime
        now_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        meta_content = {'version': '1.0',
                        'url': response.meta.get('enter_url'),
                        'crawler_method': 2,
                        'keywords': response.meta.get('keywords'),
                        'creator': 'kll',
                        'create_time': now_time,
                        'last_update_time': now_time,
                        'app_name': 'baiduNews',
                        }
        news_item = response.meta.get('intro')
        if response.body_as_unicode():
            news_res = json.loads(response.body_as_unicode())
            if news_res['errno'] == 0:  # and news_res['data'] != 'false'
                item = BaiduLoader(news_item)
                item.add_value('content', news_res)
                item.add_value('meta', meta_content)
                news_item = item.load_item()
                if not news_item.get('content'):
                    return None
        return news_item
# 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数
# 第二个参数以某种人为的方式衡量时间
schedule = sched.scheduler(time.time, time.sleep)


def run_task():
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    # from twisted.internet import reactor

    process = CrawlerProcess(get_project_settings())
    process.crawl(BaidunewsSpider)
    process.start()
    process.stop()
    # file = open('scrapy.log', 'r')
    # text = 'has finished'
    # send_ms(text)


def perform_command(inc):
    schedule.enter(inc, 0, perform_command, (inc,))
    start_time = datetime.datetime.now()
    print('start at {0}'.format(start_time))
    run_task()
    end_time = datetime.datetime.now()
    print('end at {0}'.format(end_time))


def timming_exe(inc):
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动
    schedule.enter(0, 0, perform_command, (inc,))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()

if __name__ == '__main__':
    # timming_exe(86400)
    # timming_exe(86400)
    run_task()
    # if __name__ == '__main__':
    #     scheduler = BlockingScheduler()
    #     scheduler.add_executor('processpool')
    #     # scheduler.misfire_grace_time(60)
    #     scheduler.add_job(run_task, 'interval', seconds=60, misfire_grace_time=60)
    #
    #     try:
    #         scheduler.start()
    #     except (KeyboardInterrupt, SystemExit):
    #         pass

