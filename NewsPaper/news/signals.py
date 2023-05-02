from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import (User, PostCategory)

@receiver(m2m_changed, sender=PostCategory)
def category_assigned_to_post(instance, action, **kwargs):
  if not instance.isnews:
    #print('ЭТО НЕ НОВОСТЬ!')
    return
  
  if action != 'post_add':
    #print('рановато еще')
    return

  emails = User.objects.filter(
        subscriptions__category__in = [c for c in instance.categories.all()]
    ).values_list('email', flat=True)

  subject = f'Опубликована новость "{instance}"'

  text_content = (
    f'Новость: {instance}\n'
    f'Ссылка: http://127.0.0.1:8000{instance.get_absolute_url()}'
  )

  html_content = (
    f'Новость: {instance}<br>'
    f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
    f'Ссылка</a>'
  )

  for email in emails:
    msg = EmailMultiAlternatives(subject, text_content, None, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
