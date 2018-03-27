from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import View

from DailyFresh import settings


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


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        view_fun = super().as_view()
        view_fun = login_required(view_fun)
        return view_fun


def skip_page(request):
    next = request.GET.get('next')
    if next:
        return redirect(next)
    else:
        return redirect(reverse('goods:index'))
