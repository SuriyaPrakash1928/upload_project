from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register_teacher', views.register_teacher, name='register_teacher'),
    path('register_student', views.register_student, name='register_student'),
    path('login/', views.login_view, name='login'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Student management
    path('dashboard/edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('dashboard/delete-student/<int:student_id>/', views.delete_student, name='delete_student'),

    # Teacher management
    path('dashboard/edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('dashboard/delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('dashboard/approve-teacher/<int:teacher_id>/', views.approve_teacher, name='approve_teacher'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
