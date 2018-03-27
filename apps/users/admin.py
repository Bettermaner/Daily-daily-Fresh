from django.contrib import admin

# Register your models here.
from apps.goods.models import GoodsCategory, GoodsSPU, GoodsSKU, GoodsImage, IndexCategoryGoods, IndexSlideGoods, \
    IndexPromotion
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import TestModes, User, Address


class TestmodesAdmin(admin.ModelAdmin):
    list_display = [
        'status',
        'desc'
    ]


class UserAdmin(admin.ModelAdmin):
    list_display = [
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


class AddressAdmin(admin.ModelAdmin):
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


class GoodsCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'logo',
        'image',
    ]


class GoodsSPUAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'desc'
    ]


class GoodsSKUAdmin(admin.ModelAdmin):
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


class GoodsImageAdmin(admin.ModelAdmin):
    list_display = [
        'image',
        'sku'
    ]


class IndexCategoryGoodsAdmin(admin.ModelAdmin):
    list_display = [
        'display_type',
        'category',
        'index',
        'sku',
    ]


class IndexSlideGoodsAdmin(admin.ModelAdmin):
    list_display = [
        'image',
        'index',
        'sku',
    ]


class IndexPromotionAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'image',
        'index',
        'url',
    ]


class OrderInfoAdmin(admin.ModelAdmin):
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


class OrderGoodsAdmin(admin.ModelAdmin):
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
