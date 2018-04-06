from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import *
from utils.common import LoginRequiredMixin


class IndexView(View):
    def get(self, request):

        context = cache.get('index_page_data')
        if context is None:
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
                cache.set('index_page_data', context, 3600)

        else:
            print('使用缓存')

        cart_count = 0
        if request.user.is_authenticated():
            id = request.user.id
            strict_redis = get_redis_connection('default')
            key = 'cart_%s' % id
            cart_list = strict_redis.hvals(key)
            for count in cart_list:
                cart_count += int(count)

        context.update(cart_count=cart_count)

        return render(request, 'index.html', context)


class DetailView(View):
    def get(self, request, sku_id):
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        categories = GoodsCategory.objects.all()
        new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[0:2]
        other_skus = GoodsSKU.objects.filter(spu=sku.spu).exclude(id=sku.id)

        cart_count = 0
        if request.user.is_authenticated():
            id = request.user.id
            strict_redis = get_redis_connection('default')
            key = 'cart_%s' % id
            cart_list = strict_redis.hvals(key)
            for count in cart_list:
                cart_count += int(count)

            key = 'history_%s' % id
            strict_redis.lrem(key, 1, sku.id)
            strict_redis.lpush(key, sku.id)
            strict_redis.ltrim(key, 0, 4)

        context = {
            'categories': categories,
            'sku': sku,
            'new_skus': new_skus,
            'other_skus': other_skus,
            'cart_count': cart_count,
        }
        return render(request, 'detail.html', context)


class ListView(View):
    def get(self, request, category_id, page_num):
        sort = request.GET.get('sort', 'default')
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return redirect(reverse('goods:index'))
        categories = GoodsCategory.objects.all()

        new_skus = GoodsSKU.objects.filter(category=category).order_by('-create_time')[0:2]

        if sort == 'price':
            skus = GoodsSKU.objects.filter(category=category).order_by('price')
        elif sort == 'sales':
            skus = GoodsSKU.objects.filter(category=category).order_by('-sales')
        else:
            skus = GoodsSKU.objects.filter(category=category)
            sort = 'default'

        page_num = int(page_num)
        paginator = Paginator(skus, 2)
        try:
            page = paginator.page(page_num)
        except EmptyPage:
            page = paginator.page(1)

        page_list = paginator.page_range

        cart_count = 0
        if request.user.is_authenticated():
            strict_redis = get_redis_connection('default')
            key = 'cart_%s' % request.user.id
            cart_list = strict_redis.hvals(key)
            for count in cart_list:
                cart_count += int(count)

        context = {
            'category': category,
            'categories': categories,
            'page': page,
            'new_skus': new_skus,
            'page_list': page_list,
            'cart_count': cart_count,
            'sort': sort,

        }
        return render(request, 'list.html', context)


