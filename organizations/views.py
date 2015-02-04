from braces.views import LoginRequiredMixin, JsonRequestResponseMixin,\
    AjaxResponseMixin, SetHeadlineMixin


from django.views.generic.edit import CreateView, UpdateView, DeleteView,\
    FormView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy

from organizations.forms import StudentCreateForm, GroupCreateForm,\
    ContactEditForm, SchoolAddStudentForm,\
    SchoolAddAdvisorForm, GroupNameEditForm, GroupMembershipEditForm,\
    SchoolCreateForm
from organizations.models import School, Group
from accounts.models import Student, Advisor
from django.contrib.auth.models import User
from copy import deepcopy
from django.http.response import HttpResponseRedirect
from django.views.generic.base import View, TemplateView, RedirectView
from accounts.utils import get_user_role


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupCreateForm
    template_name = 'organizations/create_group.html'
    success_url = reverse_lazy('organizations:list_group') # ('app_name:urls name')

    def get_context_data(self, **kwargs):
        data = super(GroupCreateView, self).get_context_data(**kwargs)
        data['schools'] = School.objects.all()
        return data
    
    def form_valid(self, form):
        group = form.save(commit=False)
        group.created_by = self.request.user
        group.save()

        # set this new group to all the selected members
        data = form.cleaned_data
        for phone in data['phone_numbers'].split(','):
            if phone:
                user = User.objects.get(username=phone)
                person = get_user_role(user)
                person.groups.add(group)    # don't need to save this because it's many-to-many field
        
        return super(GroupCreateView, self).form_valid(form)


class GroupMembershipEditView(LoginRequiredMixin, SetHeadlineMixin, FormView):
    form_class = GroupMembershipEditForm
    template_name = 'organizations/edit_group_member.html'

    def get_headline(self):
        group = Group.objects.get(id=self.request.GET['group_id'])
        return 'Manage Memebership of %s'%group.name

    def get_success_url(self):
        return reverse_lazy('organizations:edit_group_member') + '?group_id=' + self.request.GET['group_id'] 
    
    def get_context_data(self, **kwargs):
        data = super(GroupMembershipEditView, self).get_context_data(**kwargs)
        group = Group.objects.get(id=self.request.GET['group_id'])
        data['group'] = group
        
        data['students'] = list(Student.objects.filter(groups=group))
        data['advisors'] = list(Advisor.objects.filter(groups=group))
        data['schools'] = list(School.objects.all())
        data['all_users'] = data['students'] + data['advisors'] 
        return data

    def form_valid(self, form):
        data = form.cleaned_data
        group = Group.objects.get(id=self.request.GET['group_id'])

        for phone in data['phone_numbers'].split(','):
            phone = phone.strip()
            user = User.objects.get(username=phone)
            person = get_user_role(user)
            # if the group is not in the student groups, we add it
            if group not in person.groups.all():
                person.groups.add(group)       # Note: don't need to save bcoz ManyToMany
                
        return HttpResponseRedirect(self.get_success_url())


class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'organizations/list_group.html'
    paginate_by = 15

class GroupNameEditView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupNameEditForm
    template_name = 'organizations/edit_group_name.html'
    success_url = reverse_lazy('organizations:list_group')


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('organizations:list_group')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class SchoolCreateView(LoginRequiredMixin, CreateView):
    model = School
    form_class = SchoolCreateForm
    template_name = 'organizations/create_school.html'
    success_url = reverse_lazy('organizations:list_school')


class SchoolListView(LoginRequiredMixin, ListView):
    model = School
    template_name = 'organizations/list_school.html'
    paginate_by = 15


class SchoolEditView(LoginRequiredMixin, UpdateView):
    model = School
    form_class = SchoolCreateForm
    template_name = 'organizations/edit_school.html'
    success_url = reverse_lazy('organizations:list_school')


class SchoolDeleteMemberView(LoginRequiredMixin, DeleteView):
    model = User
    
    def get_success_url(self):
        return reverse_lazy('organizations:list_student') + '?school_id=' + self.request.GET['school_id'] 
    
    # This is to prevent us to taking ot another page and be asked to confirm if we want to delete
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class ContactEditView(LoginRequiredMixin, UpdateView):  # UpdateView will pass down object of the model, which is "School" in this case
    model = School
    form_class = ContactEditForm
    template_name = 'organizations/edit_contact.html'
    success_url = reverse_lazy('organizations:list_school')


class PersonRemoveView(LoginRequiredMixin, RedirectView):
    permanent = False   # if permanent is True and if we refresh page, they will not actually request, but instead use the browser cache, so we want it to be false

    def get_redirect_url(self, *args, **kwargs):
        # delete stu here and redirect to the same page
        user = User.objects.get(id=self.request.GET['user_id'])
        person = get_user_role(user)
        group = Group.objects.get(id=self.request.GET['group_id'])
        person.groups.remove(group)                    # DONT need to save because ManyToMany field auto saves (because student is not changed in changing ManyToMany)
        return reverse_lazy('organizations:edit_group_member') + '?group_id=' + self.request.GET['group_id']


class StudentCreateView(LoginRequiredMixin, CreateView):    # Update, Create, DeleteViews are all used for single object update 
    model = Student
    form_class = StudentCreateForm
    template_name = 'organizations/create_student.html'
    success_url = reverse_lazy('organizations:list_student') # ('app_name:urls name')

    def form_valid(self, form):
        data = form.cleaned_data
        student = form.save(commit=False) # save whatever we captured for student
        groups = []
#         for group in data['groups']:
#             groups.append(student.school.group_set.get(name=group))
        for phone in data['phone_numbers'].split(','):
            stu = deepcopy(student)
            user = User(username=phone)
            user.save()
            stu.user = user # then overwrite "user" attribute for student
            stu.save() # and save for real
            stu.groups = groups
            self.object = stu
        
        return HttpResponseRedirect(self.get_success_url())


# TODO: change this name to StudentAddView or something; Above StudentCreateView is no longer used
class StudentListView(LoginRequiredMixin, FormView):
    form_class = SchoolAddStudentForm
    template_name = 'organizations/list_student.html'

    def get_success_url(self):
        return reverse_lazy('organizations:list_student') + '?school_id=' + self.request.GET['school_id'] 
    
    def get_context_data(self, **kwargs):
        data = super(StudentListView, self).get_context_data(**kwargs)
        school = School.objects.get(id=self.request.GET['school_id'])
        data['school'] = school
        data['students'] = list(Student.objects.filter(school=school))
        return data

    def form_valid(self, form):
        data = form.cleaned_data
        for phone in data['phone_numbers'].split(','):
            phone = phone.strip()
            # TODO: BUG here. We don't check if the user is 
            # from the same school. If the user already exists 
            # in another school, we should prompt user and let
            # her know that this user already belongs to a different school 
            # and she must remove her there first before adding it to here
            if not User.objects.filter(username=phone).exists():
                user = User(username=phone)
                user.save()
                person = Student(user=user)
                person.school = School.objects.get(id=self.request.GET['school_id'])
                person.role = data['role']
                person.save()
        
        return HttpResponseRedirect(self.get_success_url())


class GroupManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'organizations/manage_groups.html'

    def get_context_data(self, **kwargs):
        data = super(GroupManagementView, self).get_context_data(**kwargs)
        data['groups'] = Group.objects.all()
        return data


class ListStudentByGroupView(LoginRequiredMixin, JsonRequestResponseMixin, AjaxResponseMixin, View):
    def get_ajax(self, request, *args, **kwargs):
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        students = Student.objects.filter(groups=group)
        groups_json = [{'username': stu.username} for stu in students]
        return self.render_json_response(groups_json)


class ListMembersBySchoolView(LoginRequiredMixin, JsonRequestResponseMixin, AjaxResponseMixin, View):
    def get_ajax(self, request, *args, **kwargs):
        school_id = request.GET.get('school_id')
        school = School.objects.get(id=school_id)
        advisors = list(Advisor.objects.filter(school=school))
        students = list(Student.objects.filter(school=school))
        members_json = [{'phone_num': stu.user.username, 'role': stu.get_role_display(), 'school': school.name} for stu in students]
        members_json += [{'phone_num': adv.user.username, 'role': 'Advisor', 'school': school.name} for adv in advisors]

        return self.render_json_response(members_json)


class AdvisorListView(LoginRequiredMixin, FormView):
    form_class = SchoolAddAdvisorForm
    template_name = 'organizations/list_advisor.html'
    
    def get_success_url(self):
        return reverse_lazy('organizations:list_advisor') + '?school_id=' + self.request.GET['school_id'] 

    def get_context_data(self, **kwargs):
        data = super(AdvisorListView, self).get_context_data(**kwargs)
        school = School.objects.get(id=self.request.GET['school_id'])
        data['school'] = school
        data['advisors'] = list(Advisor.objects.filter(school=school))
        return data

    def form_valid(self, form):
        data = form.cleaned_data
        for phone in data['phone_numbers'].split(','):
            phone = phone.strip()
            if not User.objects.filter(username=phone).exists():
                user = User(username=phone)
                user.save()
                person = Advisor(user=user)
                person.school = School.objects.get(id=self.request.GET['school_id'])
                person.save()

        return HttpResponseRedirect(self.get_success_url())


class SchoolDeleteAdvisorView(LoginRequiredMixin, DeleteView):
    model = User
    
    def get_success_url(self):
        return reverse_lazy('organizations:list_advisor') + '?school_id=' + self.request.GET['school_id'] 
    
    # This is to prevent us to taking ot another page and be asked to confirm if we want to delete
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
