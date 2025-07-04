from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Student, Teacher, Course, User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from .forms import LoginForm
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
from .models import Student, Course, Attendance, Mark, Department
from django.db.models import Count
from collections import Counter
from main.models import Department


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_superuser:
                messages.success(request, "Admin login successful!")
                return redirect('admin_dashboard')

            elif hasattr(user, 'teacher'):
                teacher = Teacher.objects.get(user=user)
                if teacher.approved:
                    messages.success(request, "Teacher login successful!")
                    return redirect('teacher_dashboard')
                else:
                    messages.warning(request, "Your teacher account is not approved yet.")
                    return redirect('login')

            elif hasattr(user, 'student'):
                messages.success(request, "Student login successful!")
                return redirect('student_dashboard')

            else:
                messages.warning(request, "No role associated with your account.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'main/login.html')


@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect('login')

    courses = Course.objects.all()
    attendance_records = Attendance.objects.filter(student=student)

    total_days = attendance_records.count()
    present_days = attendance_records.filter(status=True).count()
    attendance_percentage = round((present_days / total_days) * 100, 2) if total_days > 0 else 0

    marks = Mark.objects.filter(student=student)

    context = {
        'student' : student,
        'courses': courses,
        'attendance_records': attendance_records,
        'attendance_percentage': attendance_percentage,
        'marks': marks,
    }

    return render(request, 'main/student_dashboard.html', context)



@login_required
def teacher_dashboard(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "You are not registered as a teacher.")
        return redirect('login')
    if not teacher.approved:
        messages.warning(request, "Your account is not approved yet.")
        return redirect('login')

    students = Student.objects.filter(department=teacher.department)
    attendance = Attendance.objects.filter(student__in=students)
    marks = Mark.objects.filter(student__in=students)

    context = {
        'teacher': teacher,
        'students': students,
        'attendance': attendance,
        'marks': marks,
    }
    return render(request, 'main/teacher_dashboard.html', context)


@login_required
def admin_dashboard(request):
    students = Student.objects.all()
    teachers = Teacher.objects.all()

    # Count students and teachers per department
    student_dept_counts = students.values('department').annotate(count=Count('department'))
    teacher_dept_counts = teachers.values('department').annotate(count=Count('department'))

    teacher_dept = teachers
    return render(request, 'main/admin_dashboard.html', {
        'students': students,
        'teachers': teachers,
        'teacher_dept':teacher_dept,
        'student_dept_counts': student_dept_counts,
        'teacher_dept_counts': teacher_dept_counts,
    })

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.contact = request.POST.get('contact')
        student.department = request.POST.get('department')

        # Update User model (linked via OneToOne)
        email = request.POST.get('email')
        student.user.email = email
        student.user.username = email  # Ensure username is also updated if using email as username
        student.user.save()

        student.save()

        messages.success(request, 'Student details updated successfully.')
        return redirect('admin_dashboard')

    return render(request, 'main/edit_student.html', {'student': student})


# Edit Teacher
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        teacher.name = request.POST.get('name')
        teacher.contact_number = request.POST.get('contact_number')
        department_name = request.POST['department']
        try:
            department = Department.objects.get(name=department_name)
            teacher.department = department
        except Department.DoesNotExist:
             messages.error(request, 'Selected department does not exist.')
        teacher.skills = request.POST.get('skills')

        # Update User model
        email = request.POST.get('email')
        teacher.user.email = email
        teacher.user.username = email
        teacher.user.save()

        teacher.save()

        messages.success(request, 'Teacher details updated successfully.')
        return redirect('admin_dashboard')

    return render(request, 'main/edit_teacher.html', {'teacher': teacher})

# Delete Student
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.user.delete()  # Delete linked User too
    student.delete()
    messages.success(request, 'Student deleted successfully.')
    return redirect('admin_dashboard')

# Edit Teacher
# def edit_teacher(request, teacher_id):
#     teacher = get_object_or_404(Teacher, id=teacher_id)
#     if request.method == 'POST':
#         teacher.name = request.POST['name']
#         teacher.contact_number = request.POST['contact_number']
#         teacher.department = request.POST['department']
#         teacher.skills = request.POST['skills']
#         teacher.user.email = request.POST['email']
#         teacher.user.username = request.POST['email']
#         teacher.user.save()
#         teacher.save()
#         messages.success(request, 'Teacher updated successfully.')
#         return redirect('admin_dashboard')
#     return render(request, 'main/edit_teacher.html', {'teacher': teacher})

# Delete Teacher
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.user.delete()
    teacher.delete()
    messages.success(request, 'Teacher deleted successfully.')
    return redirect('admin_dashboard')

# Approve Teacher
def approve_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.approved = True
    teacher.save()
    messages.success(request, 'Teacher approved.')
    return redirect('admin_dashboard')


def home(request):
    return render(request, 'main/home.html')


def register_options(request):
    return render(request, 'main/register.html')


def register_teacher(request):
    if request.method == 'POST':
        # Safely get form data with fallback values
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        contact = request.POST.get('contact', '').strip()
        dob = request.POST.get('dob', '').strip()
        skills = request.POST.get('skills', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        department_id = request.POST.get('department', '').strip()

        # ✅ Check for empty required fields
        if not all([name, email, contact, dob, skills, password, confirm_password, department_id]):
            messages.error(request, "All fields are required.")
            return redirect('register_teacher')

        # ✅ Password match validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register_teacher')

        # ✅ Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('register_teacher')

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            messages.error(request, "Selected department is invalid.")
            return redirect('register_teacher')

        # ✅ Create user account
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)

        # ✅ Create teacher profile (initially not approved)
        Teacher.objects.create(
            user=user,
            name=name,
            contact=contact,
            dob=dob,
            skills=skills,
            department=department,
            approved=False  # Set to false until approved by admin
        )

        messages.success(request, "Registration successful! Wait for admin approval.")
        return redirect('login')

    departments = Department.objects.all()
    return render(request, 'main/register_teacher.html', {'departments': departments})




User = get_user_model()

from .models import Student, Course  

from django.contrib import messages
from .models import Student

def register_student(request):
    if request.method == 'POST':
        # Safely get form values
        name = request.POST.get('name', '').strip()
        dob = request.POST.get('dob', '').strip()
        contact = request.POST.get('contact', '').strip()
        email = request.POST.get('email', '').strip()
        department = request.POST.get('department', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        selected_courses = request.POST.getlist('courses')

        # ✅ Server-side empty field validation
        if not all([name, dob, contact, email, department, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return redirect('register_student')

        # ✅ Password match check
        if password != confirm_password:
            messages.warning(request, "Passwords do not match.")
            return redirect('register_student')

        # ✅ Email duplication check
        if Student.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('register_student')

        # ✅ Create user (only after validation)
        user = User.objects.create_user(username=email, email=email, password=password)

        # ✅ Create student profile
        student = Student.objects.create(
            user=user,
            name=name,
            dob=dob,
            contact=contact,
            email=email,
            department=department,
            password=password  # Optional, if storing
        )

        # ✅ Assign courses (if selected)
        for course_id in selected_courses:
            try:
                course = Course.objects.get(id=course_id)
                student.courses.add(course)
            except Course.DoesNotExist:
                continue

        messages.success(request, "Student registered successfully.")
        return redirect('login')

    return render(request, 'main/register_student.html', {'courses': Course.objects.all()})


    

# def logout_view(request):
#     return render(request, 'main/logout.html')

