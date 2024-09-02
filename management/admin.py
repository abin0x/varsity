from django.contrib import admin
from .models import Course, Enrollment, Assignment, Notification,AssignmentSubmission,BlogPost,ResearchPaper,CRNotification,Attendance

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'description')
    search_fields = ('title', 'description')
    list_filter = ('instructor',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course')
    search_fields = ('student__username', 'course__title')
    list_filter = ('course', 'student')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date')
    search_fields = ('title', 'course__title')
    list_filter = ('course', 'due_date')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'message')
    list_filter = ('course', 'created_at')

admin.site.register(AssignmentSubmission)
admin.site.register(BlogPost)
admin.site.register(ResearchPaper)
admin.site.register(CRNotification)
admin.site.register(Attendance)