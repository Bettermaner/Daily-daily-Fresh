from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU
from utils.common import LoginRequiredMixin


class CartInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        strict_redis = get_redis_connection()
        key = 'cart_%s' % user_id
        cart_dic = strict_redis.hgetall(key)
        skus = []
        total_count = 0
        total_amount = 0
        for sku_id, count in cart_dic.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            sku.count = count
            sku.amount = int(count) * sku.price
            total_count += int(count)
            total_amount += int(count) * sku.price
            skus.append(sku)

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,

        }

        return render(request, 'Cart.html', context)


class CartAddView(View):
    def post(self, request):

        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'error': '请先登录'})

        user_id = request.user.id
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        if not all([sku_id, count]):
            return JsonResponse({'code': 2, 'error': '参数不完整'})

        try:
            count = int(count)
        except:
            return JsonResponse({'code': 3, 'errmsg': '购买数量格式不正确'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 4, 'errmsg': '商品不存在'})

        strict_redis = get_redis_connection()
        key = 'cart_%s' % user_id
        val = strict_redis.hget(key, sku_id)
        if val:
            count += int(val)
        if count > sku.stock:
            return JsonResponse({'code': 5, 'error': '库存不足'})
        strict_redis.hset(key, sku_id, count)

        cart_list = strict_redis.hvals(key)
        cart_count = 0
        for val in cart_list:
            cart_count += int(val)
        return JsonResponse({'code': 0, 'message': '添加成功', 'cart_count': cart_count})


class UpdateCartView(View):
    def post(self, request):
        user_id = request.user.id
        sku_id = request.POST.get('sku_id')
        fin_num = request.POST.get('fin_num')
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'error': '请先登录'})
        if not all([sku_id, fin_num]):
            return JsonResponse({'code': 2, 'error': '参数不完整'})
        try:
            fin_num = int(fin_num)
        except Exception:
            return JsonResponse({'code': 3, 'error': '购买数量格式不正确'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 4, 'error': '商品不存在'})

        if fin_num > sku.stock:
            return JsonResponse({'code': 5, 'error': '库存不足'})

        strcit_redis = get_redis_connection()
        key = 'cart_%s' % user_id
        strcit_redis.hset(key, sku_id, fin_num)

        total_count = 0
        my_list = strcit_redis.hvals(key)
        for val in my_list:
            total_count += int(val)
        print(total_count)
        # 响应请求: 返回json数据
        return JsonResponse({'code': 0, 'message': '修改商品数量成功',
                             'total_count': total_count})


class DeleteCartView(View):
    def post(self, request):

        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'error': '请先登录'})
        user_id = request.user.id
        sku_id = request.POST.get('sku_id')
        if not all([sku_id]):
            return JsonResponse({'code': 2, 'error': '参数不完整'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 3, 'error': '商品不存在'})
        strict_redis = get_redis_connection()
        key = 'cart_%s' % user_id
        strict_redis.hdel(key, sku_id)
        return JsonResponse({'code': 0, 'message': '删除商品成功'})
