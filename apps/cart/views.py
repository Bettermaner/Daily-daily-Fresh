from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from utils.common import LoginRequiredMixin


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'Cart.html')
