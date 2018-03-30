import re

from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from DailyFresh import settings
from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
# from utils.common import send_active_email
from celery_tasks.tasks import send_active_email
from utils.common import LoginRequiredMixin, skip_page


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([username, password, password2, email]):
            return render(request, 'register.html', {'message': '参数不完整'})

        if password != password2:
            return render(request, 'register.html', {'message': '两次输入的密码不一致'})

        if allow != 'on':
            return render(request, 'register.html', {'message': '请勾选同意协议'})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'message': '邮箱格式有误'})

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            User.objects.filter(id=user.id).update(is_active=False)
        except IntegrityError:
            return render(request, 'register.html', {'message': '用户名已存在'})

        token = user.generate_active_token()
        print(token)
        send_active_email.delay(username, email, token)

        return HttpResponseRedirect(reverse('users:login'))


class ActiveView(View):
    def get(self, request, token):

        try:
            serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600)
            info = serializer.loads(token)
            user_id = info['confirm']
        except SignatureExpired:
            return HttpResponse('激活码已过期')

        User.objects.filter(id=user_id).update(is_active=True)

        return HttpResponseRedirect(reverse('users:login'))


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        if not all([username, password]):
            return render(request, 'login.html', {'message': '用户名或密码为空'})

        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'message': '用户名或密码错误'})

        if user.is_active == False:
            return render(request, 'login.html', {'message': '用户名未激活'})

        login(request, user)

        if remember:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        return skip_page(request)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('goods:index'))


class UserView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        try:
            address = user.address_set.latest('create_time')
        except Address.DoesNotExist:
            address = None

        strict_redis = get_redis_connection('default')
        key = 'history_%s' % user.id
        goods_ids = strict_redis.lrange(key, 0, 4)
        print(goods_ids)

        skus = []
        for id in goods_ids:
            print(id)
            try:
                sku = GoodsSKU.objects.get(id=id)
                skus.append(sku)
            except  GoodsSKU.DoesNotExist:
                pass
            http = 'http://127.0.0.1:8888/'
        data = {
            'skus': skus,
            'address': address,
            'http':http
        }

        return render(request, 'user.html', data)


class OrderView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order.html')


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            # 方法一
            user = request.user
            # address = Address.objects.filter(user=user).order_by('-create_time')[0]
            # 方法二
            address = user.address_set.latest('create_time')
        except Exception:
            address = None

        return render(request, 'address.html', {'address': address})

    def post(self, request):
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')
        # 获取request中的访问客户的对象
        user = request.user
        if not all([receiver, address, zip_code, mobile]):
            return render(request, 'address.html', {'message': '信息不完整'})

        Address.objects.create(receiver_name=receiver,
                               receiver_mobile=mobile,
                               detail_addr=address,
                               zip_code=zip_code,
                               user=user)

        return HttpResponseRedirect(reverse('users:address'))
