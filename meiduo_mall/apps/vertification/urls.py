from django.conf.urls import url
from .views import VerifyView, GetSmsView, CheckMObileView


urlpatterns = [
    url(r'^vertify/(?P<uuid>[\w-]+)/$', VerifyView.as_view(), name='verify'),
    url(r'^get_sms_code/$', GetSmsView.as_view(), name='get_sms'),
    url(r'^check_mobile/$', CheckMObileView.as_view(), name='check_mobile'),
]