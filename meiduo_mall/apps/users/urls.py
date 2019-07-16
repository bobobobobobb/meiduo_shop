from django.conf.urls import url

from .views import RegisterView, UserCenterSiteView, UsernameCount, LoginView, SeeStateView, UserCenterView, LogoutView, SendEmailView, ActiveUrlView

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^register/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', UsernameCount.as_view(), name='username'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^center/$', UserCenterView.as_view(), name='center'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^save_email/$', SendEmailView.as_view(), name='email'),
    url(r'^email_active/$', ActiveUrlView.as_view(), name='email_active'),
    url(r'^see_state/$', SeeStateView.as_view(), name='see_state'),
    url(r'^site/$', UserCenterSiteView.as_view(), name='site'),
]