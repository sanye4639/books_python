# -*- coding: utf-8 -*-
import scrapy
from books_python.items import BooksDetailItem
from scrapy.linkextractors import LinkExtractor

class BookSpider(scrapy.Spider):
    name = 'book'
    start_urls = ['https://m.biquge.info/sort.html']

    def parse(self, response):
        # 小说分类链接
        le = LinkExtractor(restrict_css='section.sorttop')
        # yield scrapy.Request('https://m.biquge.info/list/1_1.html', callback=self.parse_book_list)
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_book_list)

    #小说详情
    def parse_book_list(self,response):
        le = LinkExtractor(restrict_css='section.list')
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_book_detail)

        # 提取下一页的连接
        le = LinkExtractor(restrict_css='div.page')
        links = le.extract_links(response)
        if links:
            for link in links:
                if link.text == '下页':
                    yield scrapy.Request(link.url, callback=self.parse_book_list)

    #详情
    def parse_book_detail(self,response):
        book = BooksDetailItem()
        sel = response.css('div.block_txt2')
        book['name'] = sel.xpath('.//h2/text()').extract_first()

        book['writer'] = sel.xpath('./p[2]/text()').extract_first()

        book['type'] =  sel.xpath('./p[3]/a/text()').extract_first()

        book['over'] =  sel.xpath('./p[4]/text()').extract_first()

        book['new_chapter'] =  sel.xpath('./p[6]/a/text()').extract_first()

        book['pic'] = response.css('div.block_img2').xpath('./img/@src').extract_first()

        book['intro'] = response.css('div.intro_info::text').extract_first()

        book['url'] = response.url

        # print(book)
        yield book