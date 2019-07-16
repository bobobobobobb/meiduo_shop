from django.conf.urls import url
from .views import QAuthView, OauthCallBack

urlpatterns = [
    url(r'^qq_login/$', QAuthView.as_view(), name='qq_login'),
    url(r'^oauth_callback/$', OauthCallBack.as_view(), name='oauth_callback'),
]
