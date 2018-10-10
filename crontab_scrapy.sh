#!/bin/sh

/usr/bin/scrapy crawl bookChapter -a bookName=$1

echo '更新成功'