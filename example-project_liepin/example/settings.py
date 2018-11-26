# Scrapy settings for example project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
SPIDER_MODULES = ['example.spiders']
NEWSPIDER_MODULE = 'example.spiders'

ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

CONCURRENT_REQUESTS = 20

USER_AGENT = 'scrapy-redis (+https://github.com/rolando/scrapy-redis)'
# 去重类
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 配置scrapy-redis 调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

ITEM_PIPELINES = {
    # 'example.pipelines.ExamplePipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
    'example.pipelines.LaGouPipeline':500,
}

LOG_LEVEL = 'DEBUG'

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
DOWNLOAD_DELAY = 0

REDIS_HOST = '192.168.80.129'
REDIS_PORT = 6379
# REDIS_AUTH = 1234

MYSQL_INFO = {
    'host':'127.0.0.1',
    'user':'root',
    'password':'123456',
    'database':'mydb'
}
