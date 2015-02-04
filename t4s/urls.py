from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 't4s.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls', namespace='accounts', app_name='accounts')),
    url(r'^messages/', include('smsmessages.urls', namespace='smsmessages', app_name='smsmessages')),
    url(r'^organizations/', include('organizations.urls', namespace='organizations', app_name='organizations')),
    url(r'^conversations/', include('campaigns.urls', namespace='campaigns', app_name='campaigns')),
    url(r'^', include('portals.urls', namespace='portals', app_name='portals')),

)
