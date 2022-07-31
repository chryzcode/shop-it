# from __future__ import absolute_import
# import os
# from celery import Celery
# from django.conf import settings
# from celery.schedules import crontab

# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# app = Celery('core')

# # Using a string here means the worker will not have to
# # pickle the object when using Windows.
# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))

# @app.task(bind=True)
# def print_hello(self):
#     print('Hello World!')


# app.conf.beat_schedule = {
#     'add-every-24-hour' : {
#         'task': 'hello',
#         'schedule': crontab(minute='*/1')
#     }
# }