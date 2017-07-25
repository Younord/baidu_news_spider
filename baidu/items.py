# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, SelectJmes, Identity


class BaiduItem(scrapy.Item):
    # define the fields for your item here like:
    # category = scrapy.Field()  # 爬虫类别
    # source_web = scrapy.Field()  # 爬虫源站点名
    # way = scrapy.Field()  # 爬虫方式（2搜关键字）

    meta = scrapy.Field()
    hash_id = scrapy.Field(
        key=True
    )  # link的hash值
    title = scrapy.Field()  # 新闻标题
    link = scrapy.Field()  # 新闻链接
    author = scrapy.Field()  # 新闻撰稿者
    post_time = scrapy.Field()  # 新闻发布时间
    # image_urls = scrapy.Field()
    search_word = scrapy.Field()  # 搜索关键字
    cover_urls = scrapy.Field()  # 封面图片URL
    content = scrapy.Field(
        nullable=True,
        input_processor=MapCompose(SelectJmes('data.news[0].content[].{type: type, data: data.original.url || data}')),
        output_processor=Identity()
    )  # 新闻内容 无内容的新闻在生成item时过滤


class BaiduLoader(ItemLoader):
    ItemLoader.default_item_class = BaiduItem
    default_output_processor = TakeFirst()
