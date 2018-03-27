from django.conf.urls import url, include

from apps.goods.views import IndexView

urlpatterns = [
    url(r'^index$', IndexView.as_view(), name='index'),

 ]
