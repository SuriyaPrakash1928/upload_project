from django.contrib import admin
from .models import Course, Student, Attendance, Mark, Department, Teacher

admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Mark)
admin.site.register(Department)
admin.site.register(Teacher)
