from django.conf.urls import url, include
from apps.orders.views import *
urlpatterns = [
    url(r'^place$', PlaceOrderView.as_view(), name='place'),
    url(r'^commit$', CommitOrderView.as_view(), name='commit'),
    url(r'^pay$', OrderPayView.as_view(), name='pay'),
    url(r'^check$',OrderCheckView.as_view(), name='check')
]