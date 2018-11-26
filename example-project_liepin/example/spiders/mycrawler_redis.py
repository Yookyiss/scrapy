from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from scrapy_redis.spiders import RedisCrawlSpider
import re
from example.items import LaGouItem
import time
import datetime
from datetime import timedelta

class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'mycrawler_redis'
    redis_key = 'mycrawler:start_urls'

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/\?key=.*'),follow=True),
        Rule(LinkExtractor(allow=r'job/\d+\.shtml'),follow=False,callback='parse_item'),
        Rule(LinkExtractor(allow=r'zhaopin/.*',restrict_xpaths='//div[@class="pagerbar"]'),follow=True)
    )

    num_pattern = re.compile(r'\d+')
    def parse_item(self, response):
        print(response.url)
        item = LaGouItem()
        item['job_name'] = response.xpath('//h1/text()')[0].extract()
    #
        item['salary_low'], item['salary_top'] = self.process_money(
            response.xpath('//p[@class="job-item-title"]/text()')[0].extract())
    #
        item['location'] = response.xpath('//p[@class="basic-infor"]//a/text()')[0].extract()
    #
        item['work_years_low'], item['work_years_top'] = self.process_years(
            response.xpath('//div[@class="job-qualifications"]/span/text()')[1].extract())
    #
        item['education'] = response.xpath('//div[@class="job-qualifications"]/span/text()')[0].extract()
    #
        item['nature'] = '实习' if '实习' in item['job_name'] else '全职'
    #
        item['date_time'] = self.process_issued(response.xpath('//time/text()')[0])

        item['work_desc'] = ''.join(response.xpath('//div[@class="job-item main-message job-description"]//div/text()').extract())


        try:
            item['address'] = response.xpath('//ul[@class="new-compintro"]/li[3]')[0].extract().split('：')[1].strip()
        except:
            item['address'] = 'unknown'
        # print(response.xpath('//img[@class="b2"]/@alt')[0].extract())
        item['company'] = response.xpath('//div[@class="company-logo"]/p/a/text()')[0].extract()
    #
        item['crawl_time'] = datetime.datetime.now().strftime('%Y-%m-%d')
    #
        item['url'] = response.url
    #
        item['info_from'] = '猎聘'
    #
        item['lure'] = ','.join(response.xpath('//ul[@class="comp-tag-list clearfix"]//span/text()').extract())
    #     # print(type(item['crawl_time']))
    #     item['types'] = 'IT'
        yield item

    def process_money(self, response):
        if '面议' in response:
            salary_low = 0
            salary_top = 0
        else:
            base = response.split('-')
            # print(self.num_pattern.search(base[0]).group())
            salary_low = int(self.num_pattern.search(base[0]).group()) * 10000 / 12
            salary_top = int(self.num_pattern.search(base[1]).group()) * 10000 / 12
            # print(salary_top)
        return salary_low,salary_top

    def process_years(self, response):
        if '不限' in response:
            min_works_years = 0
            max_works_years = 0
        else:
            max_works_years = 100
            # print(self.num_pattern.search(response))
            min_works_years = int(self.num_pattern.search(response).group())
        return min_works_years, max_works_years

    def process_address(self, response):
        return response[-2].split('-')[1].strip()

    def process_issued(self, response):
        if '小时' or '分钟' in response:
            date_issued = datetime.datetime.now().strftime('%Y-%m-%d')
        elif '天前' in response:
            date_issued = (datetime.datetime.now() - timedelta(days=int(response))).strftime('%Y-%m-%d')
        else:
            date_issued = response
        return date_issued