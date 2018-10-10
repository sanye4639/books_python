# -*- coding: utf-8 -*-
import scrapy
import os
from books_python.items import BooksUpdateChapterItem
import re

# 单独抓取章节内容覆盖OSS存储信息
class BookSpider(scrapy.Spider):
    name = 'updateChapter'
    # start_urls = ['https://m.biquge.info/45_45839']
    url = ''
    oss_url = ''

    def __init__(self, url=None,oss_url=None, *args, **kwargs):
        super(BookSpider, self).__init__(*args, **kwargs)
        self.url = url #获取需要的抓取的url
        self.oss_url = oss_url  # 存储在OSS的url
        # scrapy crawl updateChapter -a url=https://m.biquge.info/1_1760/5264340.html -a oss_url=books/1/武炼巅峰/4418.txt

    def start_requests(self):
        yield scrapy.Request(url=self.url,meta={'oss_url':self.oss_url}, callback=self.parse)

    def parse(self, response):
        book = BooksUpdateChapterItem()
        book['title'] = response.css('div.zhong').xpath('text()').extract_first()
        book['content'] = response.css('article#nr').xpath('string()').extract_first()
        book['oss_url'] = response.meta['oss_url']
        book['url'] = response.url
        yield book
        # print(book)
