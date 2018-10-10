#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import scrapy
import time

def get_data(bookName):
    # 打开数据库连接
    db = MySQLdb.connect('localhost', 'root', 'root', 'books', charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 使用execute方法执行SQL语句
    if not bookName:
        sql_select =  "SELECT  id,`name`,`type`,url,new_chapter from book_list where dstatus = 1 and sort > 1000 and over = 1"
    else:
        sql_select =  "SELECT  id,`name`,`type`,url,new_chapter from book_list where `name` = '%s'" % (bookName)
    cursor.execute(sql_select)
    # 使用 fetchone() 方法获取一条数据
    data = cursor.fetchall()
    # 关闭数据库连接
    db.close()

    return data

def get_chapterList(new_chapter,book_id):
    db = MySQLdb.connect('localhost', 'root', 'root', 'books', charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # # 使用execute方法执行SQL语句
    # updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # sql_update = "update book_list set new_chapter = '%s',updated_at = '%s' where id = %d" % (new_chapter,updated_at,book_id)
    # cursor.execute(sql_update)
    # db.commit()

    chapter_tableName = '%s%s%s' % ('booksChapter.`book_chapter_', book_id % 100, '`')
    cursor.execute("select url from " + chapter_tableName + " where `book_id` = %d" % (book_id))
    data = cursor.fetchall()
    urlArr = []
    if data:
        for i in data:
            urlArr.append(i[0])
    db.close()
    return urlArr
