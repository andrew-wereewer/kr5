import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore

def send_spam():
  logging.getLogger(__name__).debug('ТИК')

class Command(BaseCommand):

  def handle(self, *args, **options):
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    logger = logging.getLogger(__name__)

    scheduler.add_job(
      send_spam,
      trigger=CronTrigger(second=0), #(day_of_week="fri", hour="18"),
      id="send_spam",
      max_instances=1,
      replace_existing=True,
      )
    
    logger.debug("рассылка добавлена")

    try:
      logger.debug("Starting scheduler...")
      scheduler.start()
    except KeyboardInterrupt:
      logger.debug("Stopping scheduler...")
      scheduler.shutdown()
      logger.debug("Scheduler shut down successfully!")
