from django.conf.urls import patterns, url

from organizations.views import GroupCreateView, GroupListView, StudentCreateView, StudentListView,\
    GroupManagementView, ListStudentByGroupView, GroupNameEditView, SchoolCreateView,\
    SchoolListView, SchoolEditView, GroupMembershipEditView,\
    GroupDeleteView, ContactEditView, AdvisorListView, PersonRemoveView,\
    SchoolDeleteMemberView, SchoolDeleteAdvisorView, ListMembersBySchoolView

urlpatterns = patterns('',
    url(r'^create_group/$', GroupCreateView.as_view(), name='create_group'),
    url(r'^list_group/$', GroupListView.as_view(), name='list_group'),
    url(r'^edit_group_name/(?P<pk>\d+)/$', GroupNameEditView.as_view(), name='edit_group_name'),
    url(r'^delete_group/(?P<pk>\d+)/$', GroupDeleteView.as_view(), name='delete_group'), # for delete and update view this ?P<pk.... is the only way to go

    url(r'^create_school/$', SchoolCreateView.as_view(), name='create_school'),
    url(r'^list_school/$', SchoolListView.as_view(), name='list_school'),
    url(r'^edit_school/(?P<pk>\d+)/$', SchoolEditView.as_view(), name='edit_school'),
    url(r'^edit_contact/(?P<pk>\d+)/$', ContactEditView.as_view(), name='edit_contact'),
    url(r'^school_delete_member/(?P<pk>\d+)/$', SchoolDeleteMemberView.as_view(), name='school_delete_member'),
    url(r'^school_delete_advisor/(?P<pk>\d+)/$', SchoolDeleteAdvisorView.as_view(), name='school_delete_advisor'),

    url(r'^list_student/$', StudentListView.as_view(), name='list_student'),
    url(r'^list_advisor/$', AdvisorListView.as_view(), name='list_advisor'),
    url(r'^edit_group_member/$', GroupMembershipEditView.as_view(), name='edit_group_member'),
    url(r'^remove_person/$', PersonRemoveView.as_view(), name='remove_person'),

    url(r'^list_members_by_school/$', ListMembersBySchoolView.as_view(), name='list_members_by_school'),

    url(r'^group_management/$', GroupManagementView.as_view(), name='group_management'), # TODO: can be deleted
    url(r'^list_students_by_group/$', ListStudentByGroupView.as_view(), name='list_students_by_group'), # TODO: can be deleted
    url(r'^create_student/$', StudentCreateView.as_view(), name='create_student'), # TODO: remove this along with 'create_student.html', 'create.html'

)
