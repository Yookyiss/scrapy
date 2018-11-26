from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class DmozSpider(CrawlSpider):
    """Follow categories and extract links."""
    name = 'dmoz'
    allowed_domains = ['hao123.com']
    start_urls = ['http://www.hao123.com/']

    rules = [
        Rule(LinkExtractor(),callback='parse_directory', follow=True),
    ]

    def parse_directory(self, response):
        yield {'title' : response.css('title::text').extract()[0]}