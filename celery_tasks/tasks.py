from django.core.mail import send_mail

from DailyFresh import settings

from celery import Celery

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_email(username, receiver, token):
    subject = '天天生鲜用户激活'
    message = ''
    sender = settings.EMAIL_FROM
    receivers = [receiver]
    html_message = '<h2>尊敬的 %s, 感谢注册天天生鲜</h2>' \
                   '<p>请点击此链接激活您的帐号: ' \
                   '<a href="http://127.0.0.1:8000/users/active/%s">' \
                   'http://127.0.0.1:8000/users/active/%s</a>' \
                   % (username, token, token)
    send_mail(subject, message, sender, receivers, html_message=html_message)
