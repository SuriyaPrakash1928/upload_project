from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Extend default user model
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    # No need for separate role/email here because it's inherited

# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    contact = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    courses = models.ManyToManyField('Course') # ✅ ADD THIS LINE

    def __str__(self):
        return self.name


# Teacher Model
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # New field added
    contact = models.CharField(max_length=15, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name 

# Course Model
# class Course(models.Model):
#     name = models.CharField(max_length=100)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     attendance = models.IntegerField(default=0)
#     marks = models.IntegerField(default=0)

#     def __str__(self):
#         return f"{self.name} - {self.student.user.username}"


# models.py
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/')


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField()
    
class Mark(models.Model):  # ✅ This defines the missing model
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100)
    date = models.DateField()
    marks = models.IntegerField()