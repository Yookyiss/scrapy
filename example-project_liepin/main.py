from scrapy import cmdline
import os
# cmdline.execute('scrapy crawl dmoz'.split())


os.chdir('example/spiders')
cmdline.execute('scrapy runspider mycrawler_redis.py'.split())