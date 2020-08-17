# -*- coding: utf-8 -*-
# This module contains settings for Celery

from fad_crawl_cafef.spiders.models.constants import REDIS_HOST


# Broker settings.
broker_url = f'redis://{REDIS_HOST}:6379'

# List of modules to import when the Celery worker starts.
include = ['celery_tasks']

# Using the database to store task state and results.
result_backend = f'redis://{REDIS_HOST}:6379'

# Routing
task_routes = {
    'celery_tasks.prerun_cleanup_task': {'queue': 'corpAZ_cafef'},
    'celery_tasks.corporateAZ_cafef_task': {'queue': 'corpAZ_cafef'},
    'celery_tasks.industriestickers_cafef_task': {'queue': 'finance_cafef'},
    'celery_tasks.balancesheet_cafef_task': {'queue': 'finance_cafef'},
}
