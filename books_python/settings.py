# -*- coding: utf-8 -*-
from datetime import datetime
# Scrapy settings for books_python project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'books_python'

SPIDER_MODULES = ['books_python.spiders']
NEWSPIDER_MODULE = 'books_python.spiders'


USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

ROBOTSTXT_OBEY = False


ITEM_PIPELINES = {
    'books_python.pipelines.DuplicatesPipeline': 100,
    'books_python.pipelines.BookPipeline': 200,
    'books_python.pipelines.ChapterOSSPipeline': 300,
    'books_python.pipelines.MYSQLPipeline': 400,
}

ACCESSKEYID = "LTAIj3LUZOrjEXbQ"
ACCESSKEYSECRET = "ruwB4OmUoYPJRFYqtYlg2zNcoZM5VD"
ENDPOINT = "http://oss-cn-shenzhen.aliyuncs.com"
BUCKETNAME = "sanye666"


MYSQL_DB_NAME = "books"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"


# 文件及路径，log目录需要先建好
today = datetime.now()
log_file_path = "log/scrapy_{}_{}_{}.log".format(today.year, today.month, today.day)

LOG_FILE=log_file_path
LOG_LEVEL = "ERROR"