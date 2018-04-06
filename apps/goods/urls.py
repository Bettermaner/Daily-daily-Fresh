from django.conf.urls import url, include

from apps.goods.views import *

urlpatterns = [
    url(r'^index$', IndexView.as_view(), name='index'),
    url(r'^detail/(?P<sku_id>\d+)$', DetailView.as_view(), name='detail'),
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)$', ListView.as_view(), name='list'),

 ]
