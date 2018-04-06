from django.conf.urls import url, include

from apps.cart.views import *

urlpatterns = [
    url(r'^$', CartInfoView.as_view(), name='cart'),
    url(r'^add$', CartAddView.as_view(), name='add'),
    url(r'^update$', UpdateCartView.as_view(), name='update'),
    url(r'^delete$', DeleteCartView.as_view(), name='delete')
]