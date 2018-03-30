from django.core.cache import cache
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods
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
