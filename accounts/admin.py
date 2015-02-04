from django.contrib import admin
from accounts.models import Student, Advisor, Researcher

admin.site.register(Student)
admin.site.register(Advisor)
admin.site.register(Researcher)
