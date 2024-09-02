from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    """
    Custom permission to allow only teachers to view the dashboard.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and is a teacher
        return request.user and request.user.is_authenticated and request.user.is_teacher




class IsStudentOrTeacher(permissions.BasePermission):
    """
    Custom permission to only allow access to assignments and notifications to authenticated users.
    Teachers can create, update, or delete; students can only read.
    """

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user 
        return request.user and request.user.is_authenticated and request.user.user_type == 'teacher'

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_authenticated and request.user.user_type == 'teacher'