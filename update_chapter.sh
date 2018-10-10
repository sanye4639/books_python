#!/bin/bash

/usr/bin/scrapy crawl updateChapter -a url=$1 -a oss_url=$2

echo '更新成功'