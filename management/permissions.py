from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    
    def has_permission(self, request, view):
        # Check if the user is authenticated and is a teacher
        return request.user and request.user.is_authenticated and request.user.user_type == 'teacher'

class IsStudentOrTeacher(permissions.BasePermission):
    

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user 
        return request.user and request.user.is_authenticated and request.user.user_type == 'teacher'

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_authenticated and request.user.user_type == 'teacher'


from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    

    def has_permission(self, request, view):
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        
      
        if request.method in ['POST']:
            return request.user and request.user.is_authenticated and request.user.user_type == 'student'
        
        
        return False



from rest_framework import permissions

class IsCR(permissions.BasePermission):
    
    def has_permission(self, request, view):
        # Check if the user is authenticated and is a CR
        return request.user.is_authenticated and request.user.user_type == 'cr'


from rest_framework.permissions import BasePermission

from rest_framework.permissions import BasePermission

class IsStudentOrTeachers(BasePermission):
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False  # Anonymous users are not allowed
        
        if request.method == 'POST':
            return user.user_type == 'cr'  # Only CRs can create notifications
        
        return user.user_type in ['student', 'teacher', 'cr']  # Allow students, teachers, and CRs to view notifications

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False  # Anonymous users are not allowed
        
        if user.user_type == 'cr':
            return True  # CRs can view all notifications
        
        if user.user_type == 'student':
            return obj.for_students.filter(id=user.id).exists() or not obj.for_students.exists()
        
        if user.user_type == 'teacher':
            return obj.for_teachers.filter(id=user.id).exists() or not obj.for_teachers.exists()
        
        return False  

