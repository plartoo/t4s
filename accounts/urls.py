from django.conf.urls import patterns, url

from accounts.views import LoginView, LogoutView, RegisterView,\
    VerficationCodeView, ChangePasswordView, UserProfileView, UpdateProfileView
from django.views.generic.base import TemplateView


urlpatterns = patterns('',
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^send_verification_code/$', VerficationCodeView.as_view(), name='verify'),
    url(r'^confirm/$', TemplateView.as_view(template_name='accounts/confirm.html'), name='confirm'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^user_profile/$', UserProfileView.as_view(), name='user_profile'),
    url(r'^update_profile/$', UpdateProfileView.as_view(), name='update_profile'),
)
