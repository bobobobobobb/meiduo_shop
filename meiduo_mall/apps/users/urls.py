from django.conf.urls import url
from . import views

from .views import RegisterView, ChangePasswordView, UpdateTitleAddressView, SetDefaultAddressView, DeleteAddressView, UpdateAddressView, ShowAddressView, CreateAddressView, UserCenterSiteView, UsernameCount, LoginView, SeeStateView, UserCenterView, LogoutView, SendEmailView, ActiveUrlView

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^register/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', UsernameCount.as_view(), name='username'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^center/$', UserCenterView.as_view(), name='center'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^save_email/$', SendEmailView.as_view(), name='email'),
    url(r'^email_active/$', ActiveUrlView.as_view(), name='email_active'),
    url(r'^see_state/$', SeeStateView.as_view(), name='see_state'),
    # url(r'^site/$', UserCenterSiteView.as_view(), name='site'),
    url(r'^addresses/create/$', CreateAddressView.as_view(), name='create_address'),
    url(r'^site/$', ShowAddressView.as_view(), name='show_address'),
    url(r'^addresses/(?P<address_id>\d+)/$', UpdateAddressView.as_view(), name='update_address'),
    url(r'^address/(?P<address_id>\d+)/$', DeleteAddressView.as_view(), name='delete_address'),
    # /addresses/' + this.addresses[index].id + '/default/'  put   设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', SetDefaultAddressView.as_view(), name='set_default'),
    url(r'^addresses/(?P<address_id>\d+)/title/$', UpdateTitleAddressView.as_view(), name='title'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^browse_histories/$', views.HistoryView.as_view(), name='history'),

]

