# This module contains constants used in Spiders

import os
from dotenv import load_dotenv


# Attempt to load env vars
load_dotenv(os.path.join("", ".env"))

# Proxies list
# Implement your own list of proxies here
PRIVOXY_LOCAL_PROXY = []

# Redis constants
REDIS_PORT = 6379
try:
    REDIS_HOST = os.getenv('REDIS_HOST')
except:
    REDIS_HOST = "scraper-redis"

# User cookie
try:
    USER_COOKIE = os.getenv('USER_COOKIE')
except:
    USER_COOKIE = ""

# Other constants
LANGUAGE = "en-US"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"

CAT_ID = "0"
INDUSTRY_ID = "0"
START_PAGE = "1"
PAGE_SIZE = "50"
BUSINESSTYPE_ID = "0"

PROXIES_REDIS_KEY = "acceptedProxies"

SPIDER_EXCEPTION_COUNT_SUFFIX = "spdrexception_count"
DOWNLOADER_EXCEPTION_COUNT_SUFFIX = "dwnldrexception_count"
CRAWLED_SET_SUFFIX = "crawled_set"
ERROR_SET_SUFFIX = "error_set"
