from django.core.mail import send_mail
from django.template import loader

from DailyFresh import settings

from celery import Celery

from apps.goods.models import *

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


@app.task
def generate_static_index_html():
    categories = GoodsCategory.objects.all()
    slide_skus = IndexSlideGoods.objects.all()
    promotions = IndexPromotion.objects.all()

    for category in categories:
        text_skus = IndexCategoryGoods.objects.filter(
            category=category, display_type=0).order_by('index')
        img_skus = IndexCategoryGoods.objects.filter(
            category=category, display_type=1).order_by('index')
        # 动态地给类别新增实例属性
        category.text_skus = text_skus
        # 动态地给类别新增实例属性
        category.img_skus = img_skus
    http = 'http://127.0.0.1:8888/'
    context = {
        'categories': categories,
        'slide_skus': slide_skus,
        'promotions': promotions,
        'http': http,
    }

    template = loader.get_template('index.html')
    html_str = template.render(context)

    file_path = '/home/python/Desktop/static/index.html'

    with open(file_path, 'w') as f:
        f.write(html_str)
