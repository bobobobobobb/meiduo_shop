from django.conf.urls import url
from .views import IndexView, ErrorView


urlpatterns = [
    # url(r'^(?P<error>.*)/', ErrorView.as_view(), name='error'),
    url(r'^index/$', IndexView.as_view(), name='index'),
]