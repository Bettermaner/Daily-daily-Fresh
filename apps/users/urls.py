from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from apps.users.views import RegisterView, ActiveView, LoginView, LogoutView, UserView, OrderView, AddressView

urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name='register'),
    # url(r'^do_register$', views.do_register)
    url(r'^active/(.+)$', ActiveView.as_view(), name='active'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^user$', UserView.as_view(), name='user'),
    url(r'^order$', OrderView.as_view(), name='order'),
    url(r'^address$', AddressView.as_view(), name='address')
]
