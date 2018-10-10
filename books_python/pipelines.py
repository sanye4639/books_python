# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import re
import time
import os
import oss2
import requests
from twisted.enterprise import adbapi
from books_python.items import BooksDetailItem
from books_python.items import BooksChapterItem
from books_python.items import BooksUpdateChapterItem
from scrapy.exceptions import DropItem

class DuplicatesPipeline(object):
    def __init__(self):
        self.book_set = set()
        self.chapter_set = set()

    def process_item(self, item, spider):
        # Book
        if isinstance(item, BooksDetailItem):
            name = item['name']
            if name in self.book_set:
                raise DropItem("found: %s" % item)
            self.book_set.add(name)
        # Chapter
        if isinstance(item, BooksChapterItem):
            title = item['book_title']
            if title in self.chapter_set:
                raise DropItem("found: %s" % item)
            self.chapter_set.add(title)
        return item


class BookPipeline(object):
    type_map = {
        '玄幻小说': 1,
        '修真小说': 2,
        '都市小说': 3,
        '穿越小说': 4,
        '网游小说': 5,
        '科幻小说': 6,
    }

    def process_item(self, item, spider):
        # 作者
        writer = item.get('writer')
        if writer:
            item['writer'] = writer.split('：')[-1]
        # 状态 1连载  2完本
        over = item.get('over')
        if over:
            if over.split('：')[-1] == '完本':
                item['over'] = 2
            else:
                item['over'] = 1
        # 类型 1-玄幻,2-修真,3-都市,4-穿越,5-网游,6-科幻
        type = item.get('type')
        if type:
            item['type'] = self.type_map.get(str(type),type)

        return item


class MYSQLPipeline(object):
    def open_spider(self,spider):
        db = spider.settings.get('MYSQL_DB_NAME','books')
        host = spider.settings.get('MYSQL_HOST','localhost')
        port = spider.settings.get('MYSQL_PORT','3306')
        user = spider.settings.get('MYSQL_USER','root')
        passwd = spider.settings.get('MYSQL_PASSWORD','root')

        self.dbpool = adbapi.ConnectionPool('MySQLdb',host=host,db=db,user=user,passwd=passwd,charset='utf8')

    def close_spider(self,spider):
        self.dbpool.close()

    def process_item(self,item,spider):
        query = self.dbpool.runInteraction(self.insert_db, item)  # 调用插入的方法
        query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item

    def insert_db(self,tx,item):
        if isinstance(item, BooksDetailItem):
            tx.execute("select id from book_list where `name` = %s",[item['name']])
            result = tx.fetchone()
            if not result:
                values = (
                    item['name'],
                    item['pic'],
                    item['type'],
                    item['writer'],
                    item['intro'],
                    item['url'],
                    item['over'],
                    item['new_chapter'],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                )
                sql = 'INSERT INTO book_list(`name`,pic,`type`,writer,intro,url,over,new_chapter,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                tx.execute(sql, values)
        if isinstance(item, BooksChapterItem):
            chapter_tableName = '%s%s%s' % ('booksChapter.`book_chapter_',item['book_id']%100,'`')
            tx.execute("select id from "+chapter_tableName+" where `title` = %s", [item['book_title']])
            result = tx.fetchone()

            if not result:
                values = (
                    item['book_id'],
                    item['book_title'],
                    item['book_sort'],
                    item['oss_url'],
                    item['url'],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                )
                sql = 'INSERT INTO ' + chapter_tableName + '(`book_id`,`title`,`sort`,`oss_url`,`url`,`created_at`) VALUES (%s,%s,%s,%s,%s,%s)'
                tx.execute(sql, values)

                tx.execute("select title from " + chapter_tableName + " order by sort desc limit 1")
                result = tx.fetchone()
                # db.commit()
                update_sql = "update book_list set new_chapter = '%s',updated_at = '%s' where id = %d" % (result[0],time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),item['book_id'])
                tx.execute(update_sql)


    # 错误处理方法
    def _handle_error(self, failue, item, spider):
        print('--------------database operation exception!!-----------------')
        print('-------------------------------------------------------------')
        print(failue)

# 存储章节内容至OSS
class ChapterOSSPipeline(object):

    def process_item(self,item,spider):
        bucket = oss2.Bucket(oss2.Auth(spider.settings.get('ACCESSKEYID', 'LTAIj3LUZOrjEXbQ'), spider.settings.get('ACCESSKEYSECRET', 'ruwB4OmUoYPJRFYqtYlg2zNcoZM5VD')),
                             spider.settings.get('ENDPOINT', 'http://oss-cn-shenzhen.aliyuncs.com'),spider.settings.get('BUCKETNAME', 'sanye666'))
        # if isinstance(item, BooksDetailItem):
        #     file_name = "%s%s%s%s%s%s%s"%("books/",item['type'],'/',item['name'],'/',item['name'],'.jpg')
        #     if not bucket.object_exists(file_name):
        #         # ISOTIMEFORMAT = '%Y-%m-%d'
        #         # ext = 'jpg'
        #         # image_guid = str(random.randint(1,999999))+str(time.time()).split('.')[0]+'.'+ ext
        #         # file_name = u'image/{0}/{1}'.format(time.strftime(ISOTIMEFORMAT, time.localtime()), image_guid)
        #         # 利用requests库下载图片
        #         r = requests.get(str(item['pic']))
        #         # 上传至OSS
        #         filename = file_name.format()
        #         bucket.put_object(filename, r)
        #     item['pic'] = '%s%s'%('http://img.sanye666.xin/',file_name)
        if isinstance(item, BooksChapterItem):
            # 判断是否存在该章节
            if not bucket.object_exists(item['oss_url']):
                # 上传至OSS
                filename = item['oss_url'].format()
                bucket.put_object(filename, '%s%s%s%s'%('###',item['book_title'] , '###\n\n' , item['book_content']))

        if isinstance(item, BooksUpdateChapterItem):
            # 覆盖章节信息
            filename = item['oss_url'].format()
            bucket.put_object(filename,
                              '%s%s%s%s' % ('###', item['title'], '###\n\n', item['content']))
            # if not bucket.object_exists(item['oss_url']):
            #     bucket.put_object(filename,
            #                       '%s%s%s%s' % ('###', item['title'], '###\n\n', item['content']))
            # else:
            #     bucket.delete_object(filename)
            #     bucket.put_object(filename,
            #                       '%s%s%s%s' % ('###', item['title'], '###\n\n', item['content']))
        return item

