from django.conf.urls import patterns, url
from campaigns.views import TaskQueueListView, CampaignConversationCreateView,\
    DeleteTaskQueueView, MultipleMessageConveresationCreateView,\
    SingleMessageConversationCreateView, ConversationListView,\
    ConversationMessageTreeView, DeleteConversationView,\
    ConversationSendView, ConversationDuplicateView, ConversationTitleEditView



urlpatterns = patterns('',
    url(r'^create_single_msg/$', SingleMessageConversationCreateView.as_view(), name='create_single_msg_conv'),
    url(r'^create_conversation/$', MultipleMessageConveresationCreateView.as_view(), name='create_multiple_msg_conv'),
    url(r'^list/$', ConversationListView.as_view(), name='list'),

    # In the same order as these actions appear in conversation/list page
    url(r'^conversation_messages/$', ConversationMessageTreeView.as_view(), name='conversation_messages'),
    url(r'^send/$', ConversationSendView.as_view(), name='send'),
    url(r'^duplicate_conversation/$', ConversationDuplicateView.as_view(), name='duplicate_campaign'),
    url(r'^edit_conversation_title/(?P<pk>\d+)/$', ConversationTitleEditView.as_view(), name='edit_conversation_title'),
    url(r'^delete_conversation/$', DeleteConversationView.as_view(), name='delete_conversation'),

    url(r'^taskq/$', TaskQueueListView.as_view(), name='taskq_list'),
    url(r'^delete_taskq/$', DeleteTaskQueueView.as_view(), name='delete_taskq'),

    url(r'^create/conversation/$', CampaignConversationCreateView.as_view(), name='create_conversation'),

#     url(r'^update/(?P<pk>\d+)/$', MessageUpdateView.as_view(), name='update'),
#     url(r'^delete/(?P<pk>\d+)/$', MessageDeleteView.as_view(), name='delete'),
#     url(r'^options/create/$', AddOptionView.as_view(), name='add_option'),
#     url(r'^search/$', MessageSearchView.as_view(), name='search_messages'),

)
