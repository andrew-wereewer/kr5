import logging
from django.core.mail import EmailMultiAlternatives
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q
from django_apscheduler.jobstores import DjangoJobStore
from news.models import (Post, Subscription)
from datetime import datetime, timedelta

def send_spam():
  new_posts = Post.objects.filter(~Q(isnews=1), created__gt=datetime.today()-timedelta(days=7)).prefetch_related('categories')
  #[print(p) for p in new_posts]
  #[[print(f'post:{q}, category:{d}') for d in q.categories.all()] for q in new_posts]
  categories = new_posts.values('categories').distinct().filter(categories__isnull=False)
  #[print(f) for f in categories]
  subscriptions = Subscription.objects.filter(category__in=categories.all()).select_related('user')
  #[print(u) for u in subscriptions.all()]
  #print('\n====sending=====')
  [send_letter(sub, list(filter(None, [p if sub.category.id in [pc.id for pc in p.categories.all()] else None for p in new_posts]))) for sub in subscriptions]

def send_letter(subscription, posts):
  #print(f'\ncategory: {subscription.category.name}({subscription.category.id})')
  #print(f'user: {subscription.user.username}({subscription.user.email})')
  #[print(f"post: {p}") for p in posts]
  text_content = '\n'.join([f'Автор: {p.author.user.username}, Название: {p.title}, Опубликокана: {p.created.strftime("%d/%m/%Y")}, Ссылка: http://127.0.0.1:8000{p.get_absolute_url()}' for p in posts])
  html_content = '<ul><li>'+'</li><li>'.join([f'Автор: {p.author.user.username}, Название: <a href="http://127.0.0.1:8000{p.get_absolute_url()}>{p.title}</a>, Опубликована: {p.created.strftime("%d/%m/%Y")}</li>' for p in posts]) + '</li></ul>'
  msg = EmailMultiAlternatives(
    f'Статьи в категории {subscription.category.name} за последнюю неделю',
     text_content, None, [subscription.user.email])
  msg.attach_alternative(html_content, "text/html")
  msg.send()

class Command(BaseCommand):

  def handle(self, *args, **options):
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    logger = logging.getLogger(__name__)

    scheduler.add_job(
      send_spam,
      trigger=CronTrigger(day_of_week="fri", hour="18"),
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
