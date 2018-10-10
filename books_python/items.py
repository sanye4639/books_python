# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksDetailItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    pic = scrapy.Field()
    writer = scrapy.Field()
    intro = scrapy.Field()
    type = scrapy.Field()
    over = scrapy.Field()
    new_chapter = scrapy.Field()

class BooksChapterItem(scrapy.Item):
    book_id = scrapy.Field()
    book_name = scrapy.Field()
    book_type = scrapy.Field()
    book_sort = scrapy.Field()
    book_title = scrapy.Field()
    book_content = scrapy.Field()
    oss_url = scrapy.Field()
    url = scrapy.Field()

class BooksUpdateChapterItem(scrapy.Item):
    url = scrapy.Field()
    oss_url = scrapy.Field()
    content = scrapy.Field()
    title = scrapy.Field()
