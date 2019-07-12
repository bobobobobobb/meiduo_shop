from django.conf.urls import url

from .views import RegisterView, UsernameCount

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^register/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', UsernameCount.as_view(), name='username'),
]