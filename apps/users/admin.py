from django.contrib import admin

# Register your models here.
from django.core.cache import cache

from apps.goods.models import GoodsCategory, GoodsSPU, GoodsSKU, GoodsImage, IndexCategoryGoods, IndexSlideGoods, \
    IndexPromotion
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import TestModes, User, Address
from celery_tasks.tasks import *


class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_index_html.delay()
        cache.delete('index_page_data')
    def delete_model(self, request, obj):
        obj.delete()
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class TestmodesAdmin(BaseAdmin):
    list_display = [
        'status',
        'desc'
    ]


class UserAdmin(BaseAdmin):
    list_display = [
        'id',
        'password',
        'last_login',
        'username',
        'email',
        'is_staff',
        'is_active',
        'create_time',
        'update_time',
        'delete',

    ]


class AddressAdmin(BaseAdmin):
    list_display = [
        'create_time',
        'update_time',
        'delete',
        'receiver_name',
        'receiver_mobile',
        'detail_addr',
        'zip_code',
        'is_default',
        'user_id'
    ]


class GoodsCategoryAdmin(BaseAdmin):
    list_display = [
        'name',
        'logo',
        'image',
    ]


class GoodsSPUAdmin(BaseAdmin):
    list_display = [
        'name',
        'desc'
    ]


class GoodsSKUAdmin(BaseAdmin):
    list_display = [
        'name',
        'title',
        'unit',
        'price',
        'stock',
        'sales',
        'default_image',
        'status',
        'category',
        'spu'

    ]


class GoodsImageAdmin(BaseAdmin):
    list_display = [
        'image',
        'sku'
    ]


class IndexCategoryGoodsAdmin(BaseAdmin):
    list_display = [
        'display_type',
        'category',
        'index',
        'sku',
    ]


class IndexSlideGoodsAdmin(BaseAdmin):
    list_display = [
        'image',
        'index',
        'sku',
    ]


class IndexPromotionAdmin(BaseAdmin):
    list_display = [
        'name',
        'image',
        'index',
        'url',
    ]


class OrderInfoAdmin(BaseAdmin):
    list_display = [
        'order_id',
        'total_count',
        'total_amount',
        'trans_cost',
        'pay_method',
        'status',
        'trade_no',
        'user',
        'address',

    ]


class OrderGoodsAdmin(BaseAdmin):
    list_display = [
        'count',
        'price',
        'comment',
        'order',
        'sku',

    ]


admin.site.register(TestModes, TestmodesAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(GoodsSPU, GoodsSPUAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsImage, GoodsImageAdmin)
admin.site.register(IndexCategoryGoods, IndexCategoryGoodsAdmin)
admin.site.register(IndexSlideGoods, IndexSlideGoodsAdmin)
admin.site.register(IndexPromotion, IndexPromotionAdmin)
admin.site.register(OrderInfo, OrderInfoAdmin)
admin.site.register(OrderGoods, OrderGoodsAdmin)
