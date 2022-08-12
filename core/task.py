# from core.celery import app
# from django.template.loader import render_to_string
# from django.utils import timezone
# from datetime import datetime, timedelta


# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

# from celery.utils.log import get_task_logger

# logger = get_task_logger(__name__)

# @periodic_task(run_every=crontab(minute='*/1'), name="hello", ignore_result=True)
# def hello():
#     logger.info("Hello World")
#     print('Hello World!')
#     return 'Hello World!'
