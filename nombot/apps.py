import requests
from django.apps import AppConfig
from django.conf import settings

from .scheduler import NombotScheduler, ScheduleThread


class NombotAppConfig(AppConfig):
    name = 'nombot'
    verbose_name = 'Nombot'

    def ready(self):
        scheduler = NombotScheduler()
        continuous_thread = ScheduleThread()
        continuous_thread.start()

        # scheduler.test_job()
        scheduler.monitoring_jobs()
        scheduler.suggestion_jobs()
        scheduler.comparison_jobs()
        scheduler.competition_jobs()

        payload = {'url': settings.TELEGRAM_WEBHOOK_URL}
        requests.post("%ssetWebhook" % settings.TELEGRAM_BOT_URL, data=payload)
