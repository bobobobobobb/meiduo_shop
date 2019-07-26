from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^carts/$', views.CartView.as_view(), name='cart'),
    url(r'^carts/selection/$', views.SelectAllCartView.as_view(), name='select_all'),
    url(r'^carts/simple/$', views.ShowSimpleCartView.as_view(), name='show_simple_cart'),
]