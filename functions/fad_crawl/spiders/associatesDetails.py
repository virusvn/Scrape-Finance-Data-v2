# -*- coding: utf-8 -*-
# This spider crawls a stock ticker's associated companies/subsidiaries

import json
import logging
import os
import sys
import traceback

import requests
import redis
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str
from scrapy_redis.spiders import RedisSpider

import fad_crawl.spiders.models.utilities as utilities
from fad_crawl.spiders.models.associatesdetails import data as ass
from fad_crawl.spiders.models.associatesdetails import name, settings, report_types
from fad_crawl.spiders.fadRedis import fadRedisSpider
from fad_crawl.helpers.fileDownloader import save_jsonfile
from fad_crawl.spiders.models.corporateaz import \
    closed_redis_key as corpAZ_closed_key


class associatesHandler(fadRedisSpider):
    name = name
    custom_settings = settings

    def __init__(self, *args, **kwargs):
        super(associatesHandler, self).__init__(*args, **kwargs)
        self.ass = ass
        self.report_types = report_types
        self.ticker_report_page_count_key = f'{self.name}:trp_count'
        self.ticker_report_page_crawled_key = f'{self.name}:trp_crawled'

        self.r.set(self.ticker_report_page_count_key, "0")
        self.r.set(self.ticker_report_page_crawled_key, "0")

    def next_requests(self):
        """Replaces the default method. Closes spider when tickers are crawled and queue empty.
        Customizing this method from fadRedis Spider because it has the Page param. in formdata.
        """

        use_set = self.settings.getbool(
            'REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            # Fetch one ticker from Redis list, mark all reports for this ticker as unfinished
            data = fetch_one(self.redis_key)
            if not data:
                break

            ticker = bytes_to_str(data, self.redis_encoding)
            self.ass["formdata"]["code"] = ticker

            for report_type in self.report_types:
             # Look for number of pages for this ticker first
                try:
                    numPages = requests.post(url=self.ass["url"],
                                             data=self.ass["formdata"],
                                             headers=self.ass["headers"],
                                             cookies=self.ass["cookies"],
                                             proxies=self.ass["proxies"],
                                             verify=False
                                             ).json()[0]["TotalPage"]
                    self.logger.info(f'NumPages was calculated as {numPages}')
# If request above is not possible, assume numPages = 4
                except:
                    numPages = 4
# Increase the pages supposed to crawl by NumPages
                self.r.incr(self.ticker_report_page_count_key, numPages)
# Loop through all the pages
                for pg in range(1, numPages+1):
                    req = self.make_request_from_data(
                        ticker, report_type, page=str(pg))
                    if req:
                        yield req
                        # found += 1
                        self.r.incr(self.ticker_report_page_crawled_key, 1)
                        self.logger.info(
                            f'Dequeued {self.r.get(self.ticker_report_page_crawled_key)} ticker-report-page so far')
                    else:
                        self.logger.info(
                            "Request not made from data: %r", data)
            found += 1

# Log number of requests consumed from Redis feed
        if found:
            self.logger.debug("Read %s tickers from '%s'",
                              found, self.redis_key)

# Close spider if none in queue and amount crawled == amount dequeued
        if self.r.get(corpAZ_closed_key) == "1" and self.r.get(self.ticker_report_page_count_key) == self.r.get(self.ticker_report_page_crawled_key):
            keys = self.r.keys(f'{self.name}*')
            for k in keys:
                self.r.delete(k)
            self.crawler.engine.close_spider(
                spider=self, reason="CorpAZ is closed. Crawled everything")

    def make_request_from_data(self, ticker, report_type, page):
        """
        Replaces the default method, data is a ticker.
        """

        self.ass["formdata"]["code"] = ticker
        self.ass["formdata"]["page"] = page
        self.ass["meta"]["ticker"] = ticker
        self.ass["meta"]["ReportType"] = report_type
        self.ass["meta"]["Page"] = page

        return FormRequest(url=self.ass["url"],
                           formdata=self.ass["formdata"],
                           headers=self.ass["headers"],
                           cookies=self.ass["cookies"],
                           meta=self.ass["meta"],
                           callback=self.parse
                           )

    def parse(self, response):
        if response:
            # If response is not an empty string, save it and +1 for # of pages crawled
            try:
                resp_json = json.loads(response.text)
                ticker = response.meta['ticker']
                page = response.meta['Page']
                save_jsonfile(
                    resp_json, filename=f'localData/{self.name}/{ticker}_Page_{page}.json')
# If it is an empty string, then we've finished the report type
            except:
                self.logger.info("Response is an empty string")
