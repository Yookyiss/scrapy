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
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            "Host":" www.lagou.com",
            "Connection":" keep-alive",
            "Cache-Control":" max-age=0",
            "Upgrade-Insecure-Requests":" 1",
            "User-Agent":" Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
            "Accept":" text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer":" https://www.lagou.com/",
            # "Accept-Encoding":" gzip, deflate, br",
            "Accept-Language":" zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie":" user_trace_token=20181103224616-b35535a9-cf10-49f7-92bf-11b19280eb47; _ga=GA1.2.1350618428.1541256376; LGUID=20181103224617-38452f4f-df77-11e8-8611-525400f775ce; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22166ddde837031c-0f48bc01e3dca7-51422e1f-2073600-166ddde837246d%22%2C%22%24device_id%22%3A%22166ddde837031c-0f48bc01e3dca7-51422e1f-2073600-166ddde837246d%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; LG_LOGIN_USER_ID=59e40d8475f9cea690969ecf1d92daf329ec0a085f973c93ce29aa8027ac4310; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; _gid=GA1.2.2063257377.1541679186; JSESSIONID=ABAAABAAAGFABEFC64C72D3E9DC7A14C33C3AE98E88071F; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1541336055,1541643508,1541677467,1541750726; _putrc=BC8774DBC56BC323123F89F2B170EADC; login=true; unick=%E6%AD%A6%E9%93%9C%E8%B4%BA; X_HTTP_TOKEN=73007360b38621f1d078ebe9aa6c0327; gate_login_token=5a0a8ab5634009c08852961ba17c19312043b897cc024a2dc8e70219c47faa1c; LGSID=20181109202129-fc4d9d34-e419-11e8-8775-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2F; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; _gat=1; SEARCH_ID=d35eb24190ee458cac6c9c61fd2655f0; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_recjob; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1541766302; LGRID=20181109202459-79de8255-e41a-11e8-8775-5254005c3644"

        }
    }

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@class="menu_box"]'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'zhaopin/.*?/\d+/'),follow=True)
    )

    num_pattern = re.compile(r'\d+')
    def parse_item(self, response):
        item = LaGouItem()
        item['job_name'] = response.xpath('//span[@class="name"]/text()')[0].extract()

        item['salary_low'], item['salary_top'] = self.process_money(
            response.xpath('//span[@class="salary"]/text()')[0].extract())

        item['location'] = response.xpath('//dd[@class="job_request"]/p/span/text()')[1].extract().split('/')[1].strip()

        item['work_years_low'], item['work_years_top'] = self.process_years(
            response.xpath('//dd[@class="job_request"]/p/span/text()')[2].extract())

        item['education'] = response.xpath('//dd[@class="job_request"]/p/span/text()')[3].extract().split('/')[
            0].strip()

        item['nature'] = response.xpath('//dd[@class="job_request"]/p/span/text()')[4].extract().split('/')[0]

        item['date_time'] = self.process_issued(
            response.xpath('//p[@class="publish_time"]/text()')[0].extract().split()[0])

        item['work_desc'] = ''.join(response.xpath('//dd[@class="job_bt"]/div//p/text()').extract()).split()

        item['address'] = self.process_address(response.xpath('//div[@class="work_addr"]/text()').extract())

        item['company'] = response.xpath('//img[@class="b2"]/@alt')[0].extract()

        item['crawl_time'] = datetime.datetime.now().strftime('%Y-%m-%d')

        item['url'] = response.url

        item['info_from'] = '拉钩'

        item['lure'] = response.xpath('//dd[@class="job-advantage"]/p/text()')[0].extract()
        # print(type(item['crawl_time']))
        # item['types'] = 'IT'
        yield item

    def process_money(self, response):
        salary_low = int(response.split('-')[0].lower().split('k')[0]) * 1000
        salary_top = int(response.split('-')[1].lower().split('k')[0]) * 1000
        # print(salary_top)
        return salary_low,salary_top

    def process_years(self, response):
        # print(response)
        if '-' not in response:
            print('no')
            return 0, 0
        else:
            response = response.split('/')[0]
            list = response.split('-')
            # print(self.num_pattern.search(list[0]),'ok')
            # print(list)
            min_works_years = self.num_pattern.search(list[0]).group()
            max_works_years = self.num_pattern.search(list[1]).group()
            # print(min_works_years, max_works_years)
            return min_works_years, max_works_years

    def process_address(self, response):
        return response[-2].split('-')[1].strip()

    def process_issued(self, response):
        if '天前' in response:
            res = self.num_pattern.search(response).group()
            date_issued = (datetime.datetime.now() - timedelta(days=int(res))).strftime('%Y-%m-%d')
        elif len(response) == 5:
            date_issued = datetime.datetime.now().strftime('%Y-%m-%d')

        else:
            date_issued = response

        return date_issued