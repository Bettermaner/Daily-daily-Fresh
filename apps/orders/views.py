from time import sleep

from alipay import AliPay
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.timezone import now
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import *
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.common import LoginRequiredMixin


class PlaceOrderView(LoginRequiredMixin, View):
    def post(self, request):
        user_id = request.user.id
        sku_ids = request.POST.getlist('sku_ids')

        if not sku_ids:
            return redirect(reverse('cart:cart'))

        skus = []
        total_count = 0
        total_amount = 0
        trans_cost = 10
        total_pay = 0
        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                return redirect(reverse('cart:cart'))
            skus.append(sku)
            strict_redis = get_redis_connection()
            key = 'cart_%s' % user_id
            count = strict_redis.hget(key, sku_id.encode())
            amount = sku.price * int(count)
            sku.amount = amount
            sku.count = int(count)

            total_count += int(count)
            total_amount += amount
            total_pay = total_amount + trans_cost

        try:
            address = Address.objects.filter(user=request.user).latest('create_time')
        except Address.DoesNotExist:
            address = None

        sku_ids_str = ','.join(sku_ids)

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'trans_cost': trans_cost,
            'total_pay': total_pay,
            'address': address,
            'sku_ids_str': sku_ids_str
        }
        return render(request, 'place_order.html', context)


class CommitOrderView(View):
    @transaction.atomic
    def post(self, request):
        user_id = request.user.id
        address_id = request.POST.get('address_id')
        pay_method = request.POST.get('pay_method')
        sku_ids_str = request.POST.get('sku_ids_str')

        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'error': '请先登录'})
        if not all([address_id, sku_ids_str, pay_method]):
            return JsonResponse({'code': 2, 'error': '缺少参数'})
        try:
            address = Address.objects.get(id=address_id)
            print(address)
        except Address.DoesNotExist:
            return JsonResponse({'code': 3, 'error': '地址不存在'})

        point = transaction.savepoint()

        total_count = 0
        total_amount = 0
        trans_cost = 10
        order_id = now().strftime('%Y%m%d%H%M%S') + str(user_id)

        order = OrderInfo.objects.create(
            order_id=order_id,
            user=request.user,
            address=address,
            total_count=0,
            total_amount=0,
            trans_cost=trans_cost,
            pay_method=pay_method,
        )

        strict_redis = get_redis_connection()
        key = 'cart_%s' % user_id
        sku_ids = sku_ids_str.split(',')

        for sku_id in sku_ids:
            count = strict_redis.hget(key, sku_id.encode())

            try:
                sku = GoodsSKU.objects.get(id=sku_id)

            except GoodsSKU.DoesNotExist:
                transaction.savepoint_rollback(point)
                return JsonResponse({'code': 4, 'error': '商品不存在'})
            if sku.stock < int(count):
                transaction.savepoint_rollback(point)
                return JsonResponse({'code': 5, 'error': '库存不足'})

            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=int(count),
                price=sku.price,

            )

            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()

            total_amount += int(count) * sku.price
            total_count += int(count)

        order.total_count = total_count
        order.total_amount = total_amount
        order.save()

        transaction.savepoint_commit(point)

        for sku_id in sku_ids:
            strict_redis.hdel(key, sku_id)

        return JsonResponse({'code': 0})


class OrderPayView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'error': '请先登录'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'code': 2, 'error': '订单id不能为空'})
        try:
            order = OrderInfo.objects.get(order_id=order_id, status=1, user=request.user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 3, 'error': '订单无效'})

        app_private_key_str = open('apps/orders/app_private_key.pem').read()
        alipay_public_key_str = open('apps/orders/alipay_public_key.pem').read()

        alipay = AliPay(
            appid='2016091000481376',
            app_notify_url=None,
            app_private_key_string=app_private_key_str,
            alipay_public_key_string=alipay_public_key_str,
            sign_type='RSA2',
            debug=True,
        )

        order_pay = order.total_amount + order.trans_cost
        order_str = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order_pay),
            subject='天天生鲜支付测试',
            return_url=None,
            notify_url=None,
        )
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_str
        return JsonResponse({'code': 0, 'pay_url': pay_url})


class OrderCheckView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'error': '请先登录'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'code': 2, 'error': '订单id不能为空'})
        try:
            order = OrderInfo.objects.get(order_id=order_id, status=1, user=request.user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 3, 'error': '订单无效'})

        app_private_key_str = open('apps/orders/app_private_key.pem').read()
        alipay_public_key_str = open('apps/orders/alipay_public_key.pem').read()

        alipay = AliPay(
            appid='2016091000481376',
            app_notify_url=None,
            app_private_key_string=app_private_key_str,
            alipay_public_key_string=alipay_public_key_str,
            sign_type='RSA2',
            debug=True,
        )

        while True:

            response = alipay.api_alipay_trade_query(out_trade_no=order_id)
            code = response.get('code')
            trade_no = response.get('trade_no')
            trade_status = response.get('trade_status')

            if code == '10000' and trade_status == 'TRADE_SUCCESS':
                order.trade_no = trade_no
                order.status = 4
                order.save()
                return JsonResponse({'code': 0})
            elif code == '40004' or (code == '10000' and trade_status == 'WAIT_BUYER_PAY'):
                sleep(2)
                print(code)
                continue
            else:
                return JsonResponse({'code': 4, 'error': '支付失败'})
