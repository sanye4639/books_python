# # -*- coding: utf-8 -*-
# import scrapy
# from books_python.items import BooksDetailItem
# from books_python.items import BooksChapterItem
# import re
# import os
# import oss2
# from scrapy.utils.project import get_project_settings
# from scrapy.linkextractors import LinkExtractor
# import MySQLdb
# import time
# from twisted.enterprise import adbapi
#
# class BookSpider(scrapy.Spider):
#     name = 'book'
#     start_urls = ['https://m.biquge.info/sort.html']
#
#     def parse(self, response):
#         # 提取每本书的链接
#         le = LinkExtractor(restrict_css='section.sorttop')
#         # yield scrapy.Request('https://m.biquge.info/list/6_1.html', callback=self.parse_book_list)
#         for link in le.extract_links(response):
#             yield scrapy.Request(link.url, callback=self.parse_book_list)
#
#     #
#     def parse_book_list(self,response):
#         le = LinkExtractor(restrict_css='section.list')
#         for link in le.extract_links(response):
#             yield scrapy.Request(link.url, callback=self.parse_book_detail)
#
#         # 提取下一页的连接
#         le = LinkExtractor(restrict_css='div.page')
#         links = le.extract_links(response)
#         if links:
#             for link in links:
#                 if link.text == '下页':
#                     yield scrapy.Request(link.url, callback=self.parse_book_list)
#
#     #详情
#     def parse_book_detail(self,response):
#         book = BooksDetailItem()
#         sel = response.css('div.block_txt2')
#         book['name'] = sel.xpath('.//h2/text()').extract_first()
#
#         book['writer'] = sel.xpath('./p[2]/text()').extract_first()
#
#         book['type'] =  sel.xpath('./p[3]/a/text()').extract_first()
#
#         book['over'] =  sel.xpath('./p[4]/text()').extract_first()
#
#         book['new_chapter'] =  sel.xpath('./p[6]/a/text()').extract_first()
#
#         book['pic'] = response.css('div.block_img2').xpath('./img/@src').extract_first()
#
#         book['intro'] = response.css('div.intro_info::text').extract_first()
#
#         book['url'] = response.url
#
#         yield book
#
#
#
# # 抓取小说章节信息存入数据库，章节内容存储至OSS
# class BookSpider(scrapy.Spider):
#     name = 'bookChapter'
#     # start_urls = ['https://m.biquge.info/45_45839']
#     settings = get_project_settings()
#     db = settings.get('MYSQL_DB_NAME')
#     host = settings.get('MYSQL_HOST')
#     port = settings.get('MYSQL_PORT')
#     user = settings.get('MYSQL_USER')
#     passwd = settings.get('MYSQL_PASSWORD')
#
#     dbpool = adbapi.ConnectionPool('MySQLdb', host=host, db=db, user=user, passwd=passwd, charset='utf8')
#     auth = oss2.Auth(settings.get('ACCESSKEYID'), settings.get('ACCESSKEYSECRET'))
#     bucket = oss2.Bucket(auth, settings.get('ENDPOINT'), settings.get('BUCKETNAME'), enable_crc=False)
#     page = 0
#     datas = {}
#
#     def __init__(self, page=None, *args, **kwargs):
#         super(BookSpider, self).__init__(*args, **kwargs)
#         self.datas = self.dbpool.runInteraction(self.select_book, self.page)
#         print(self.datas)
#         # print(self.dbpool.runQuery("select id as book_id,name as book_name,type as book_type,url from book_list where `over` = 1 limit %s,10", [int(self.page)]))  # 获取需要的抓取的url
#         # self.datas = self.dbpool.runInteraction(self.select_book,page)  # scrapy crawl bookChapter -a page=0
#
#
#     def start_requests(self):
#         yield scrapy.Request(url='https://m.biquge.info/45_45839', callback=self.parse)
#         # for data in self.datas:
#             # yield scrapy.Request(url=data.url,meta=data, callback=self.parse)
#
#
#     def parse(self, response):
#         book = BooksChapterItem()
#
#         # 获取小说分类及名称
#         sel = response.css('div.block_txt2')
#         book['book_name'] = sel.xpath('//h2/text()').extract_first()
#         book['book_type'] = sel.xpath('./p[3]/a/text()').extract_first()
#         #
#         # book['book_id'] = response.meta['book_id']
#         # book['book_name'] = response.meta['book_name']
#         # book['book_type'] = response.meta['book_type']
#
#         # 测试
#         # test_url = 'https://m.biquge.info/45_45839/2965411.html'
#         # book_sort = re.findall(r'(\d+).html', test_url)[0]
#         # yield scrapy.Request(test_url, meta={'book_name': book_name, 'book_type': book_type, 'book_sort': book_sort},
#         #                      callback=self.parse_book_chapter)
#
#         # 本地判断文件是否存在
#         # path = '/home/books/public/book/'+book_type+'/'+book_name
#         # path = path.strip()
#         # path = path.rstrip("\\")
#         # isExists = os.path.exists(path)
#         # if not isExists:
#         #     os.makedirs(path)
#
#         le = LinkExtractor(restrict_css='ul:nth-last-child(2)')
#         for link in le.extract_links(response):
#             book['book_sort'] = re.findall(r'(\d+).html',link.url)[0]
#             # 判断本地文件是否存在
#             # if os.path.isfile('/home/books/public/book/' + book_type + '/' + book_name + '/' + book_sort + '.txt'):
#             # if not self.bucket.object_exists('books/'+book['book_type']+'/'+book['book_name']):
#             yield scrapy.Request(link.url,meta=book, callback=self.parse_book_chapter)
#
#         # 提取下一页的连接
#         le = LinkExtractor(restrict_css='span.right')
#         links = le.extract_links(response)
#         if links:
#             next_url = links[0].url
#             yield scrapy.Request(next_url, callback=self.parse)
#
#     def parse_book_chapter(self,response):
#         book = BooksChapterItem()
#         # book['book_id'] = response.meta['book_id']
#         book['book_id'] = 32318
#         book['book_name'] = response.meta['book_name']
#         book['book_type'] = response.meta['book_type']
#         book['book_sort']  = response.meta['book_sort']
#         book['book_title'] = response.css('div.zhong').xpath('text()').extract_first()
#         book['book_content'] = response.css('article#nr').xpath('string()').extract_first()
#         book['url'] = response.url
#
#         oss_url = "books/"+book['book_type']+"/"+book['book_name']+"/"+book['book_sort']+".txt"
#         book['oss_url'] = oss_url
#
#         # 判断是否存在该章节
#         if not self.bucket.object_exists(oss_url):
#             # 上传至OSS
#             filename = oss_url.format()
#             self.bucket.put_object(filename, '###'+book['book_title']+'###\n\n'+book['book_content'])
#             # 存储章节信息至数据库
#             self.dbpool.runInteraction(self.insert_chapter,book)
#
#         # 在本地生成文件
#         # f1 = open('/home/books/public/book/'+book_type+'/'+book_name+'/'+book_sort+'.txt', 'a')
#         # seq = ['\n\n###'+book_title+'###\n\n',book_content]
#         # f1.writelines(seq)
#
#     def insert_chapter(self,tx,book):
#         values = (
#             book['book_id'],
#             book['book_title'],
#             book['url'],
#             book['oss_url'],
#             book['book_sort'],
#             time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         )
#         # chapter_tableName = 'booksChapter.`book_chapter_' + book['book_id']%100 + '`'
#         chapter_tableName = 'booksChapter.`book_chapter_18`'
#
#         sql = 'INSERT INTO ' + chapter_tableName +'(`book_id`,title,`url`,oss_url,sort,created_at) VALUES (%s,%s,%s,%s,%s,%s)'
#         tx.execute(sql, values)
#
#     def select_book(self,tx,page):
#         tx.execute("select id as book_id,name as book_name,type as book_type,url from book_list where `over` = 1 limit %s,10", [int(page)])
#         result = tx.fetchall()
#         # for aa in result:
#         #     for a in aa:
#         #         print(a)
#         return result
#
