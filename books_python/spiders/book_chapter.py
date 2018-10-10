# -*- coding: utf-8 -*-
import scrapy
import os
import re
import logging
from books_python.items import BooksChapterItem
from scrapy.linkextractors import LinkExtractor
from books_python.db import get_data
from books_python.db import get_chapterList

# 抓取小说章节信息存入数据库，章节内容存储至OSS
class BookSpider(scrapy.Spider):
    name = 'bookChapter'
    # start_urls = ['https://m.biquge.info/45_45839']
    datas = {}
    chapterList = {}
    sort = {}

    def __init__(self, bookName=None, *args, **kwargs):
        super(BookSpider, self).__init__(*args, **kwargs)
        self.datas = get_data(bookName) #获取需要的抓取的url
         # scrapy crawl bookChapter -a bookName=元尊

    def start_requests(self):
        if not self.datas:
            print("%s%s%s" % ("'",data[1]+"'---该小说不存在"))
            logging.error("%s%s%s" % ("'",data[1]+"'---该小说不存在"))
            os._exit(0)
        for data in self.datas:
            # data[0]-id  data[1]-name  data[2]-type data[3]-url  data[4]-new_chaptert
            yield scrapy.Request(url=data[3],meta={'book_id':int(data[0]),'book_name':data[1],'book_type':int(data[2]),'new_chapter':data[4]}, callback=self.parse)


    def parse(self, response):
        sel = response.css('div.block_txt2')
        new_chapter = sel.xpath('./p[6]/a/text()').extract_first()
        # 根据小说的最新章节判断是否需要更新
        if new_chapter != response.meta['new_chapter']:
            # 获取小说已存在的章节列表
            self.chapterList = get_chapterList(new_chapter,response.meta['book_id'])

            le = LinkExtractor(restrict_css='ul:nth-last-child(2)')
            for link in le.extract_links(response):
                sort_key = '%s%s'%('book_id_',response.meta['book_id'])
                if sort_key in self.sort:
                    self.sort[sort_key] += 1
                    book_sort = self.sort.get(sort_key)
                else:
                    self.sort[sort_key] = 1
                    book_sort = 1
                # 判断该章节是否存在章节列表中
                if not self.chapterList.__contains__(link.url):
                    yield scrapy.Request(link.url,
                                         meta={'book_id': response.meta['book_id'], 'book_name': response.meta['book_name'],
                                               'book_type': response.meta['book_type'], 'book_sort': book_sort},
                                         callback=self.parse_book_chapter)
            # 提取下一页的连接
            le = LinkExtractor(restrict_css='span.right')
            links = le.extract_links(response)
            if links:
                next_url = links[0].url
                yield scrapy.Request(next_url,
                                     meta={'book_id': response.meta['book_id'], 'book_name': response.meta['book_name'],
                                           'book_type': response.meta['book_type'],
                                           'new_chapter': response.meta['new_chapter']}, callback=self.parse)
        else:
            logging.error('%s%s%s' % ("'",response.meta['book_name'],"'---该小说暂无更新"))
            print('%s%s%s' % ("'",response.meta['book_name'],"'---该小说暂无更新"))

    def parse_book_chapter(self,response):
        book = BooksChapterItem()
        book['book_id'] = response.meta['book_id']
        book['book_name'] = response.meta['book_name']
        book['book_type'] = response.meta['book_type']
        book['book_sort']  = response.meta['book_sort']
        book['book_title'] = response.css('div.zhong').xpath('text()').extract_first()
        book['book_content'] = response.css('article#nr').xpath('string()').extract_first()
        book['oss_url'] = '%s%s%s%s%s%s%s' % ('books/',book['book_type'],'/',book['book_name'],'/',book['book_sort'],'.txt')
        book['url'] = response.url
        isContent = '正在手打中'
        if isContent in book['book_content']:
            if book['book_title']:
                logging.error('%s%s%s%s%s' % ("'", response.meta['book_name'], "'---该小说章节",book['book_title'],"正在手打中"))
                print('%s%s%s%s%s' % ("'", response.meta['book_name'], "'---该小说章节",book['book_title'],"正在手打中"))
        else:
            yield book
        # print(book)
