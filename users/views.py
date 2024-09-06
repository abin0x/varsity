from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from .models import CustomUser
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.generics import RetrieveAPIView

# class UserRegistrationAPIView(APIView):
#     serializer_class = RegistrationSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
        
#         if serializer.is_valid():
#             user = serializer.save()
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             confirm_link = f"https://varsity-s41t.onrender.com/api/users/activate/{uid}/{token}/"
#             email_subject = "Confirm Your Email"
            
#             email_template = 'confirm_teacher_email.html' if user.user_type == 'teacher' else 'confirm_student_email.html'
#             email_body = render_to_string(email_template, {'confirm_link': confirm_link})
#             email = EmailMultiAlternatives(email_subject, '', to=[user.email])
#             email.attach_alternative(email_body, "text/html")
#             email.send()

#             return Response({"detail": "Check your email for confirmation"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationAPIView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate email confirmation token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"https://varsity-s41t.onrender.com/api/users/activate/{uid}/{token}/"
            email_subject = "Confirm Your Email"

            # Select email template based on user type
            if user.user_type == 'teacher':
                email_template = 'confirm_teacher_email.html'
            elif user.user_type == 'cr':
                email_template = 'confirm_cr_email.html'  # New CR email template
            else:
                email_template = 'confirm_student_email.html'

            # Render email body
            email_body = render_to_string(email_template, {'confirm_link': confirm_link})

            # Send the email
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()

            return Response({"detail": "Check your email for confirmation"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('https://hstu.netlify.app/login.html')
    else:
        return redirect('register')

class UserLoginApiView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({'key': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    def get(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)
        return Response({"detail": "Logged out successfully."})


class UserListAPIView(APIView):
    def get(self, request):
        # users = CustomUser.objects.filter(user_type='teacher')
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class UserDetailAPIView(RetrieveAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = 'pk'

# users/views.py
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from .serializers import UserSerializer
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from .permissions import IsTeacher,IsStudentOrTeacher

class UserDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsStudentOrTeacher]

    def get_object(self):
        """
        Ensure that users can only update their own profiles.
        """
        obj = super().get_object()
        if obj != self.request.user:
            raise PermissionDenied("You do not have permission to edit this user.")
        return obj

    def update(self, request, *args, **kwargs):
        """
        Handle the update of the user profile.
        """
        partial = True  # Allows partial updates
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)



from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import generics, permissions
from rest_framework.response import Response
from management.models import Enrollment, Assignment, Notification, AssignmentSubmission,BlogPost,ResearchPaper,CRNotification
from management.serializers import CourseSerializer, AssignmentSerializer, NotificationSerializer, AssignmentSubmissionSerializer,BlogPostSerializer,ResearchPaperSerializer,CRNotificationSerializer

class StudentDashboardAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access this view

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is authenticated and has the 'student' type
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({'error': 'Unauthorized'}, status=403)

        # Get the user's enrollments
        enrollments = Enrollment.objects.filter(student=user)
        courses = [enrollment.course for enrollment in enrollments]

        # Get assignments related to those courses
        # assignments = Assignment.objects.filter(course__in=courses)

        # Get assignments related to those courses
        assignments = Assignment.objects.filter(course__in=courses)

        # Get notifications for the student
        notifications = Notification.objects.filter(for_students=user)

        # Get submitted assignments
        submitted_assignments = AssignmentSubmission.objects.filter(student=user)

        # Get pending assignments
        pending_assignments = assignments.exclude(id__in=submitted_assignments.values_list('assignment', flat=True))

        blog_count = BlogPost.objects.filter(author=user).count()
        # Get the CR notifications created by the student
        # crnotifications = CRNotification.objects.filter(created_by=user)  
        crnotifications = CRNotification.objects.filter(for_students=user)

        crnotifications_count = crnotifications.count()
        # Serialize data
        assignment_serializer = AssignmentSerializer(assignments, many=True)
        course_serializer = CourseSerializer(courses, many=True)
        submitted_assignment_serializer = AssignmentSubmissionSerializer(submitted_assignments, many=True)
        pending_assignment_serializer = AssignmentSerializer(pending_assignments, many=True)
        notification_serializer = NotificationSerializer(notifications, many=True)
        crnotification_serializer = CRNotificationSerializer(crnotifications, many=True)  # Serialize crnotifications
        # Get details of blogs created by the student
        blog_posts = BlogPost.objects.filter(author=user)
        blog_post_serializer = BlogPostSerializer(blog_posts, many=True)

         # Get research papers created by the student
        research_papers = ResearchPaper.objects.filter(author=user)
        research_paper_count = research_papers.count()
        research_paper_serializer = ResearchPaperSerializer(research_papers, many=True)
        
        return Response({
            'enrolled_courses': course_serializer.data,
            'submitted_assignments': submitted_assignment_serializer.data,
            'pending_assignments': pending_assignment_serializer.data,
            'notifications': notification_serializer.data,
            'assignments': assignment_serializer.data,
            'blog_count': blog_count,
            'blogs': blog_post_serializer.data,
            'research_paper_count': research_paper_count,
            'research_papers': research_paper_serializer.data,
            'crnotifications_count': crnotifications_count,  # Add the count of crnotifications
            'crnotifications': crnotification_serializer.data,
        })





# new 

from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] 

    def get_object(self):
        # Retrieve the logged-in user
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Allow partial updates to the user profile
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
