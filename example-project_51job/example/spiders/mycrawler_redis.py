from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from scrapy_redis.spiders import RedisCrawlSpider
import re
from example.items import LaGouItem
import time
import datetime
from datetime import timedelta


# 51job
class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'mycrawler_redis'
    redis_key = 'mycrawler:start_urls'
    rules = (
        Rule(LinkExtractor(allow=r'',restrict_xpaths='//div[@class="hcity"]'),follow=True),
        Rule(LinkExtractor(allow=r'com/list/.*?,.*?,.*?,.*?,9,99,.*'),follow=True,process_links='process_link'),
        Rule(LinkExtractor(allow=r'jobs.*?s=01&t=0'),follow=False,callback='parse_item')
    )

    num_pattern = re.compile(r'\d+')
    def process_link(self,links):
        for link in links:
            link.url = link.url.split('?')[0]
        return links

    def parse_item(self, response):
        print(response.url)
        item = LaGouItem()
        item['job_name'] = response.xpath('//h1/text()')[0].extract().strip()
    #
        item['salary_low'], item['salary_top'] = self.process_money(
            response.xpath('//div[@class="cn"]//strong/text()').extract())
    #
        item['location'] = response.xpath('//p[@class="msg ltype"]/@title')[0].extract().split('|')[0].strip()
    #
        item['work_years_low'], item['work_years_top'] = self.process_years(response.xpath('//p[@class="msg ltype"]/@title')[0].extract().split('|')[1].strip())
    #
        item['education'] = self.process_education(response.xpath('//p[@class="msg ltype"]/@title')[0].extract().split('|')[2].strip())
    #
        item['nature'] = '实习' if '实习' in item['job_name'] else '全职'
    #
        item['date_time'] = self.process_issued(
            response.xpath('//p[@class="msg ltype"]/@title')[0].extract().split('|'))
    #
        item['work_desc'] = response.xpath('//div[@class="bmsg job_msg inbox"]')[0]
        item['work_desc'] = item['work_desc'].xpath('string(.)').extract()[0].split('职能类别')[0].strip()

        try:
            item['address'] = response.xpath('//div[@class="bmsg inbox"]//p')[0]
            item['address'] = item['address'].xpath('string(.)').extract()[0].strip()
        except:
            item['address'] = 'unknown'
        # print(item['address'],'yk')
    #
        item['company'] = response.xpath('//div[@class="com_msg"]//p/text()')[0].extract().strip()
    #
        item['crawl_time'] = datetime.datetime.now().strftime('%Y-%m-%d')
    # split('')
        item['url'] = response.url
    #
        item['info_from'] = '51job'
    #
        item['lure'] = ','.join(response.xpath('//div[@class="t1"]/span/text()').extract())
        if item['lure'] == '':
            item['lure'] = 'unknown'

    #     # print(type(item['crawl_time']))
        yield item
    #
    def process_money(self, response):
        # print(response)
        try:
            response = response[0]
        
            if '千' in response:
                if '以下' in response:
                    salary_low = 0
                    salary_top = float(response.split('以')[0]) * 1000
                else:
                    base = response.split('千')[0].split('-')
                    salary_low = float(base[0]) * 1000
                    salary_top = float(base[1]) * 1000
            elif '万' in response:
                base = response.split('万')[0].split('-')
                salary_low = float(base[0]) * 10000
                salary_top = float(base[1]) * 10000
                if '年' in response:
                    salary_top = salary_top / 12
                    salary_low = salary_low / 12
    
    
            else:
                salary_low = '0'
                salary_top = '0'
        except:
            salary_low = '0'
            salary_top = '0'
        # print('salary',salary_top)
        return int(salary_low),int(salary_top)

    def process_years(self, response):
        if '-' not in response:
            if '无工作' in response:
                return 0, 0
            else:
                base = response
                return self.num_pattern.search(base).group(),self.num_pattern.search(base).group()
        else:
            list = response.split('-')
            # print(self.num_pattern.search(list[0]),'ok')
            # print(list)
            min_works_years = self.num_pattern.search(list[0]).group()
            max_works_years = self.num_pattern.search(list[1]).group()
            # print('years',min_works_years, max_works_years)
            return min_works_years, max_works_years


    def process_issued(self,response):
        date = 'unknown'
        for i in response:
            if '发布' in i:
                date = i.split('发')[0].strip()
                date = '2018-' + date
        # print(date)
        return date

    def process_education(self,response):
        if '招' in response:
            return 'nuknown'
        else:
            return response
