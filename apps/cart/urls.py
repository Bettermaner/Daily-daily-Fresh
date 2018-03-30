from django.conf.urls import url, include

from apps.cart.views import CartView

urlpatterns = [
    url(r'^cart$', CartView.as_view(), name='cart')
]