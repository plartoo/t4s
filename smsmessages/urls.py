from django.conf.urls import patterns, url

from smsmessages.views import MessageListView, MessageUpdateView, MessageDeleteView,\
    MessageReceiveView, TaskQueueConversationView,\
    UserConversationView
from smsmessages.views import AddOptionView, MessageSearchView


urlpatterns = patterns('',
    url(r'^list/$', MessageListView.as_view(), name='list'),
    url(r'^update/(?P<pk>\d+)/$', MessageUpdateView.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', MessageDeleteView.as_view(), name='delete'),
    url(r'^options/create/$', AddOptionView.as_view(), name='add_option'),
    url(r'^search/$', MessageSearchView.as_view(), name='search_messages'),
    url(r'^receive/$', MessageReceiveView.as_view(), name='receive_messages'),
    url(r'^view_conversation/$', UserConversationView.as_view(), name='view_conversation'),
    url(r'^taskq_conversation/$', TaskQueueConversationView.as_view(), name='taskq_conversation'),
)
