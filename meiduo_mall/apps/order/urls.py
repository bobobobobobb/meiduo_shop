from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/settlement/$', views.PlaceOrderView.as_view(), name='place_order'),
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='order_commit'),
    url(r'^orders/success/$', views.OrderSuccess.as_view(), name='order_success'),
]
