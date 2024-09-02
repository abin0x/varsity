from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
User = get_user_model()

def validate_course_title(value):
    if len(value) < 5:
        raise ValidationError('Course title must be at least 5 characters long.')

class Course(models.Model):
    title = models.CharField(max_length=100, validators=[validate_course_title])
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    department = models.CharField(max_length=100,default='eee')
    description = models.TextField()
    course_code = models.CharField(max_length=10, blank=True, null=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name='assignments')
    for_students = models.ManyToManyField(User, limit_choices_to={'user_type': 'student'}, blank=True)

    def __str__(self):
        return self.title

from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)
    teacher_name = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'teacher'},
        related_name='notifications_as_teacher'  # Unique related_name
    )
    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    for_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'user_type': 'student'},
        blank=True,
        related_name='notifications_as_student' 
    )

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, related_name='submissions')
    description = models.TextField(blank=True, null=True)  
    submitted_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    image_url = models.URLField(blank=True, null=True)  # New field for image URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class ResearchPaper(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    document = models.FileField(upload_to='research_papers/')
    img_url = models.URLField(max_length=500, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

from django.db import models
from django.conf import settings

class CRNotification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)  # Optional
    course_code = models.CharField(max_length=20, null=True, blank=True)  # Optional field for course code
    # creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user_type': 'cr'})
    file = models.FileField(upload_to='cr_notifications/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'user_type': 'cr'},
        related_name='cr_notifications_created'
    )
    for_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        limit_choices_to={'user_type': 'student'}, 
        related_name='cr_notifications_as_student', 
        blank=True
    )
    for_teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        limit_choices_to={'user_type': 'teacher'}, 
        related_name='cr_notifications_as_teacher', 
        blank=True
    )

    def __str__(self):
        return self.title



class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'}, related_name='student_attendance')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    present = models.BooleanField(default=False)
    # cr = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'cr'}, related_name='cr_attendance')
    cr = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cr_attendance')

    class Meta:
        unique_together = ('student', 'course', 'date', 'cr')

    def __str__(self):
        return f'{self.student.username} - {self.course.title} - {self.date}'