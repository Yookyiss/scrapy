# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import scrapy


class ExampleItem(Item):
    name = Field()
    description = Field()
    link = Field()
    crawled = Field()
    spider = Field()
    url = Field()


class ExampleLoader(ItemLoader):
    default_item_class = ExampleItem
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    description_out = Join()

class LaGouItem(scrapy.Item):
    job_name = scrapy.Field()
    salary_top = scrapy.Field()
    salary_low = scrapy.Field()
    location = scrapy.Field()
    work_years_top = scrapy.Field()
    work_years_low = scrapy.Field()
    education = scrapy.Field()
    nature = scrapy.Field()
    lure = scrapy.Field()
    work_desc = scrapy.Field()
    address = scrapy.Field()
    company = scrapy.Field()
    crawl_time = scrapy.Field()
    url = scrapy.Field()
    date_time = scrapy.Field()
    info_from = scrapy.Field()