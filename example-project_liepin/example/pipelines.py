# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from datetime import datetime
import pymysql


class ExamplePipeline(object):
    def process_item(self, item, spider):
        item["crawled"] = datetime.utcnow()
        item["spider"] = spider.name
        return item

class LaGouPipeline(object):
    def __init__(self,crawler):
        self.crawler = crawler
        self.mysql_info = self.crawler.settings["MYSQL_INFO"]

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)

    def process_item(self,item,spider):
        self.connect = pymysql.connect(self.mysql_info["host"],self.mysql_info["user"],self.mysql_info["password"],self.mysql_info["database"])
        cursor = self.connect.cursor()
        sql = 'insert into job_copy(url,job_name,salary_low,salary_top,location,work_years_low,work_years_top,education,nature,info_from,date_time,work_desc,address,company,crawl_time,lure) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update salary_low=VALUES(salary_low),salary_top=values(salary_top)'
        # print(sql % (item["url"],item["job_name"],item["salary_low"],item["salary_top"],item["location"],item["work_years_low"],item["work_years_top"],item["education"],item["nature"],item["info_from"],item["date_time"],''.join(item["work_desc"]),item["address"],item["company"],item["crawl_time"],item['lure']))
        # print(sql % (item["url"],item["job_name"],item["salary_low"],item["salary_top"],item["location"],item["work_years_low"],item["work_years_top"],item["education"],item["nature"],item["info_from"],item["work_lure"],''.join(item["work_desc"]),item["address"],item["company"],item["crawl_time"]))

        cursor.execute(sql,(item["url"],item["job_name"],item["salary_low"],item["salary_top"],item["location"],item["work_years_low"],item["work_years_top"],item["education"],item["nature"],item["info_from"],item["date_time"],''.join(item["work_desc"]),item["address"],item["company"],item["crawl_time"],item['lure']))
        self.connect.commit()
    def close_spider(self,spider):
        self.connect.close()
