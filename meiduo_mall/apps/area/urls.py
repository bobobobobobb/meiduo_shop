from django.conf.urls import url
from .views import AreasView


urlpatterns = [

    url(r'^area/$', AreasView.as_view(), name='area'),

]