from hashlib import new
from rest_framework import serializers
from .models import Course, Enrollment, Assignment, Notification,AssignmentSubmission,ResearchPaper,BlogPost
from django.contrib.auth import get_user_model
User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'department', 'description', 'course_code', 'image_url', 'created_at']
        read_only_fields = ['instructor', 'created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'course']

    def validate(self, attrs):
        student = self.context['request'].user
        course = attrs.get('course')

        # Ensure the user is a student
        if student.user_type != 'student':
            raise serializers.ValidationError("Only students can enroll.")

        # Check if the student is already enrolled in the course
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")

        return attrs

class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'course']
        # fields = ['id', 'title', 'description', 'due_date', 'course', 'for_students']


class NotificationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    teacher_name = serializers.StringRelatedField()  # Display the teacher's name
    for_students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Read-only field

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'course', 'course_title', 'course_code', 'teacher_name', 'created_at', 'for_students']

    def create(self, validated_data):
        teacher = self.context['request'].user  # Get the teacher creating the notification

        # Remove teacher_name from validated_data
        validated_data.pop('teacher_name', None)

        # Create the notification with teacher_name set separately
        notification = Notification.objects.create(teacher_name=teacher, **validated_data)

        # Automatically assign all students to the notification
        all_students = User.objects.filter(user_type='student')
        notification.for_students.set(all_students)

        return notification

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'image_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Ensure the author is set to the current user
        request = self.context.get('request')
        if request and request.user:
            validated_data['author'] = request.user
        return super().create(validated_data)



class TeacherDashboardSerializer(serializers.Serializer):
    courses_created = serializers.IntegerField()
    assignments_created = serializers.IntegerField()
    notifications_created = serializers.IntegerField()
    student_count_per_course = serializers.DictField(child=serializers.IntegerField())
    assignment_submission_count = serializers.DictField(child=serializers.IntegerField())
    
    

        
class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer()
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'student', 'assignment','description', 'submitted_file', 'submitted_at']
        


# new 

class AssignmentSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = [ 'assignment', 'description', 'submitted_file']

    def validate_assignment(self, value):
        if not Assignment.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Assignment does not exist.")
        return value


class ResearchPaperSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = ResearchPaper
        fields = ['id', 'title', 'author', 'content', 'document','img_url', 'created_at', 'updated_at']



from rest_framework import serializers
from .models import CRNotification, Course
from django.contrib.auth import get_user_model

User = get_user_model()

class CRNotificationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True, required=False)
    course_code = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)  # Optional
    created_by = serializers.StringRelatedField(read_only=True)  
    for_teachers = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='teacher'), many=True, required=False)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CRNotification
        fields = ['id', 'title', 'description', 'course', 'course_title', 'course_code', 'file','file_url', 'created_at', 'created_by', 'for_students', 'for_teachers']
        read_only_fields = ['id', 'created_at', 'created_by', 'course_title', 'for_students']

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

    def create(self, validated_data):
        cr = self.context['request'].user  # Get the CR creating the notification

        # Remove creator from validated_data
        # validated_data.pop('creator', None)

        # Ensure the user is a student
        if cr.user_type != 'cr':
            raise serializers.ValidationError("Only CRs (students) can create notifications.")

        # Pop the for_teachers field from validated_data, if present
        teachers = validated_data.pop('for_teachers', None)

        # Create the notification with or without course details
        # notification = CRNotification.objects.create(created_by=cr, **validated_data)
        # Create the notification without `created_by`
        notification = CRNotification.objects.create(**validated_data)
        # Set `created_by` manually
        notification.created_by = cr
        notification.save()

        # Assign all students to the notification by default
        all_students = User.objects.filter(user_type='student')
        notification.for_students.set(all_students)

        # Optionally assign specific teachers to the notification
        if teachers:
            notification.for_teachers.set(teachers)

        return notification



from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['course', 'student', 'cr', 'date', 'present']


