from rest_framework import generics, permissions, serializers
from rest_framework import generics, permissions
from .models import Course, Enrollment, Assignment, Notification
from .serializers import CourseSerializer, EnrollmentSerializer, AssignmentSerializer, NotificationSerializer,AssignmentSubmissionSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.conf import settings
from .permissions import IsStudent
import logging
from rest_framework.exceptions import NotFound

User = get_user_model()
from .permissions import IsTeacher, IsStudentOrTeacher

class CourseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsStudentOrTeacher] 

    def perform_create(self, serializer):
        # Automatically set the instructor to the currently logged-in user
        serializer.save(instructor=self.request.user)

    def get_queryset(self):
        queryset = Course.objects.all()
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department=department)
        return queryset

class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class EnrollmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudent] 


    def perform_create(self, serializer):
        student = self.request.user
        course = serializer.validated_data.get('course')

        
        if student.user_type != 'student':
            raise serializers.ValidationError("Only students can enroll.")

        # Check if the student is already enrolled in the course
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")

        # Save the enrollment with the current student
        serializer.save(student=student)


class AssignmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsStudentOrTeacher]

    def perform_create(self, serializer):
        # Save the assignment
        assignment = serializer.save()

        # Create a notification
        notification_title = f"New Assignment Created: {assignment.title}"
        notification_message = f"An assignment titled '{assignment.title}' has been created for the course '{assignment.course.title}'. Please check your dashboard for details."

        # Get students who are enrolled in the course
        enrolled_students = User.objects.filter(
            user_type='student',
            enrollment__course=assignment.course
        ).distinct()

        student_emails = enrolled_students.values_list('email', flat=True)

        # Create the notification
        notification = Notification.objects.create(
            title=notification_title,
            message=notification_message,
            course=assignment.course,
            teacher_name=self.request.user,
            assignment=assignment,
        )

        # Assign the enrolled students to the notification
        notification.for_students.set(enrolled_students)

        # Send email to each enrolled student
        subject = notification_title
        html_message = render_to_string('email/assignment_notification.html', {'notification': notification})
        plain_message = strip_tags(html_message)
        from_email = 'mahmhdulabin@gmail.com'  # Use your actual email

        # Send email
        send_mail(subject, plain_message, from_email, list(student_emails), html_message=html_message)

class AssignmentDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsTeacher]

    def perform_update(self, serializer):
        # Save the updated assignment
        assignment = serializer.save()

        # Notify students about the update
        self.notify_students(assignment)

    def notify_students(self, assignment):
        # Create a notification
        notification_title = f"Assignment Updated: {assignment.title}"
        notification_message = f"An assignment titled '{assignment.title}' has been updated for the course '{assignment.course.title}'. Please check your dashboard for details."

        # Get students who are enrolled in the course
        enrolled_students = User.objects.filter(
            user_type='student',
            enrollment__course=assignment.course
        ).distinct()

        student_emails = enrolled_students.values_list('email', flat=True)

        # Create the notification
        notification = Notification.objects.create(
            title=notification_title,
            message=notification_message,
            course=assignment.course,
            teacher_name=self.request.user,
            assignment=assignment,
        )

        # Assign the enrolled students to the notification
        notification.for_students.set(enrolled_students)

        # Prepare the email
        subject = notification_title
        html_message = render_to_string('email/assignment_notification.html', {'notification': notification})
        plain_message = strip_tags(html_message)
        from_email = 'mahmhdulabin@gmail.com'  # Use your actual email

        send_mail(subject, plain_message, from_email, list(student_emails), html_message=html_message)


class NotificationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsStudentOrTeacher]

    def perform_create(self, serializer):
        # Save the notification object with the teacher as the creator
        notification = serializer.save(teacher_name=self.request.user)

        # Automatically select all students and associate them with the notification
        all_students = User.objects.filter(user_type='student')
        notification.for_students.set(all_students)

        # Sending email to each student
        for student in all_students:
            subject = f"New Notification: {notification.title}"
            html_message = render_to_string('email/notification_email.html', {'notification': notification})
            plain_message = strip_tags(html_message)
            from_email = 'mahmhdulabin@gmail.com'  # Use your actual email
            recipient_list = [student.email]

            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

        # Save the notification after setting all students
        notification.save()

class NotificationDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsTeacher]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.teacher_name:
            raise permissions.PermissionDenied("You do not have permission to edit this notification.")
        return obj

    def perform_update(self, serializer):
        # Update the notification
        notification = serializer.save()

        # Send email to each student
        students = notification.for_students.all()
        subject = f"Notification Updated: {notification.title}"
        html_message = render_to_string('email/notification_email.html', {'notification': notification})
        plain_message = strip_tags(html_message)
        from_email = 'mahmhdulabin@gmail.com'  # Use your actual email
        recipient_list = [student.email for student in students]

        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

class NotificationSearchAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        course_code = self.kwargs.get('course_code')
        if not course_code:
            return Notification.objects.none()  # Return an empty queryset if no course_code is provided

        notifications = Notification.objects.filter(course__course_code=course_code)
        if not notifications.exists():
            raise NotFound('No notifications found for this course code.')
        return notifications


class AssignmentSearchAPIView(generics.ListAPIView):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        course_code = self.request.query_params.get('course_code')
        course_title = self.request.query_params.get('course_title')

        if not course_code and not course_title:
            return Assignment.objects.none()  # Return an empty queryset if no filters are provided

        # Filter assignments based on course_code and course_title
        queryset = Assignment.objects.all()

        if course_code:
            queryset = queryset.filter(course__course_code=course_code)
        if course_title:
            queryset = queryset.filter(course__title__icontains=course_title)

        if not queryset.exists():
            raise NotFound('No assignments found for the provided search criteria.')

        return queryset

logger = logging.getLogger(__name__)
class AssignmentSearchByCourseAPIView(generics.ListAPIView):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        search_param = self.kwargs.get('search_param')
        logger.info(f"Search parameter received: {search_param}")

        # Filter assignments based on course_code or course_title
        queryset = Assignment.objects.filter(
            course__course_code__icontains=search_param
        ) | Assignment.objects.filter(
            course__title__icontains=search_param
        )

        if not queryset.exists():
            logger.warning(f"No assignments found for search parameter: {search_param}")
            raise NotFound('No assignments found for the provided search criteria.')

        logger.info(f"Assignments found: {queryset}")
        return queryset


from django.core.mail import EmailMessage

class SubmitAssignmentAPIView(generics.CreateAPIView):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):
        submission = serializer.save()
        
        # Notify the teacher about the submission
        self.notify_teacher(submission)

    def notify_teacher(self, submission):
        assignment = submission.assignment
        teacher = assignment.course.instructor
        student = submission.student

        subject = f"New Assignment Submission: {assignment.title}"
        html_message = render_to_string('email/assignment_submission.html', {
            'assignment': assignment,
            'student': student,
            'submission': submission,
            'description': submission.description,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [teacher.email]

        # Create the email message with attachment
        email = EmailMessage(subject, plain_message, from_email, recipient_list)
        email.content_subtype = 'html'  # Specify that the email content is HTML
        
        # Attach the submitted file
        if submission.submitted_file:
            email.attach_file(submission.submitted_file.path)
        
        email.send()

        # abin 


class TeacherDashboardAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access this view

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is authenticated and has the 'teacher' type
        if not hasattr(user, 'user_type') or user.user_type != 'teacher':
            return Response({'error': 'Unauthorized'}, status=403)

        # Get the courses created by the teacher
        created_courses = Course.objects.filter(instructor=user)
        course_serializer = CourseSerializer(created_courses, many=True)

        # Get assignments created by the teacher
        created_assignments = Assignment.objects.filter(course__in=created_courses)
        assignment_serializer = AssignmentSerializer(created_assignments, many=True)

        # Get notifications created by the teacher
        created_notifications = Notification.objects.filter(teacher_name=user)
        notification_serializer = NotificationSerializer(created_notifications, many=True)

       

        # Count students enrolled in each course
        courses = Course.objects.filter(instructor=user)
        student_count_per_course = {course.title: Enrollment.objects.filter(course=course).count() for course in courses}

        
        # Count submissions for each assignment
        assignments = Assignment.objects.filter(course__in=courses)
        assignment_submission_count = {assignment.title: AssignmentSubmission.objects.filter(assignment=assignment).count() for assignment in assignments}

        # Get blog posts created by the teacher
        blog_posts = BlogPost.objects.filter(author=user)
        blog_post_serializer = BlogPostSerializer(blog_posts, many=True)
        blog_count = BlogPost.objects.filter(author=user).count()
        # Get research papers created by the teacher
        research_papers = ResearchPaper.objects.filter(author=user)
        research_paper_count = research_papers.count()
        research_paper_serializer = ResearchPaperSerializer(research_papers, many=True)

        # Get CR notifications created by the teacher
        # cr_notifications = CRNotification.objects.filter(created_by=user)
        cr_notifications = CRNotification.objects.filter(for_teachers=user) | CRNotification.objects.filter(for_teachers=None)
        cr_notification_serializer = CRNotificationSerializer(cr_notifications, many=True)
        cr_notification_count = cr_notifications.count()

        return Response({
            'courses_created': course_serializer.data,
            'assignments_created': assignment_serializer.data,
            'notifications_created': notification_serializer.data,
            'student_count_per_course': student_count_per_course,
            'assignment_submission_count': assignment_submission_count,
            'blog_count': blog_count,
            'blogs': blog_post_serializer.data,
            'research_paper_count': research_paper_count,
            'research_papers': research_paper_serializer.data,
            'cr_notification_count': cr_notification_count,
            'cr_notifications': cr_notification_serializer.data,
        })
    


from rest_framework.permissions import IsAuthenticated
from .permissions import IsTeacher

class StudentCountPerCourseAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.user_type != 'teacher':
            return Response({'error': 'Unauthorized'}, status=403)

        courses = Course.objects.filter(instructor=user)
        student_count_per_course = {course.title: Enrollment.objects.filter(course=course).count() for course in courses}

        return Response(student_count_per_course, status=status.HTTP_200_OK)




class AssignmentSubmissionCountAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.user_type != 'teacher':
            return Response({'error': 'Unauthorized'}, status=403)

        courses = Course.objects.filter(instructor=user)
        assignments = Assignment.objects.filter(course__in=courses)
        assignment_submission_count = {assignment.title: AssignmentSubmission.objects.filter(assignment=assignment).count() for assignment in assignments}

        return Response(assignment_submission_count, status=status.HTTP_200_OK)


# another 
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Assignment, AssignmentSubmission
from .serializers import AssignmentSerializer, AssignmentSubmissionCreateSerializer

class AssignmentListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student = self.request.user
        enrolled_courses = student.courses.all()  # Assuming a student has a 'courses' related name for their enrollments
        assignments = Assignment.objects.filter(course__in=enrolled_courses)
        
        # Exclude assignments that the student has already submitted
        submitted_assignments = AssignmentSubmission.objects.filter(student=student).values_list('assignment_id', flat=True)
        assignments = assignments.exclude(id__in=submitted_assignments)
        
        return assignments

class SubmitAssignmentView(generics.CreateAPIView):
    serializer_class = AssignmentSubmissionCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AssignmentSubmission.objects.none()

    def perform_create(self, serializer):
        student = self.request.user
        assignment = serializer.validated_data.get('assignment')
        
        # Check if the student has already submitted the assignment
        if AssignmentSubmission.objects.filter(student=student, assignment=assignment).exists():
            raise ValidationError("You have already submitted this assignment.")
        
        # Save the submission
        submission = serializer.save(student=student)
        
        # Notify the teacher about the submission
        self.notify_teacher(submission)

    def notify_teacher(self, submission):
        assignment = submission.assignment
        teacher = assignment.course.instructor
        student = submission.student

        subject = f"New Assignment Submission: {assignment.title}"
        html_message = render_to_string('email/assignment_submission.html', {
            'assignment': assignment,
            'student': student,
            'submission': submission,
            'description': submission.description,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [teacher.email]

        # Create the email message with attachment
        email = EmailMessage(subject, plain_message, from_email, recipient_list)
        email.content_subtype = 'html'  # Specify that the email content is HTML

        # Attach the submitted file
        if submission.submitted_file:
            email.attach_file(submission.submitted_file.path)
        
        email.send()



# blog/views.py

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BlogPost
from .serializers import BlogPostSerializer
from django.http import HttpResponse, HttpResponseNotFound, Http404

class BlogPostList(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = BlogPost.objects.all().order_by('-created_at')
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Set the author to the current user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlogPostDetail(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = BlogPostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk):
        post = self.get_object(pk)
        # Check if the current user is the author of the post
        if post.author != request.user:
            return Response({'detail': 'You do not have permission to edit this post.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BlogPostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        post = self.get_object(pk)
        # Check if the current user is the author of the post
        if post.author != request.user:
            return Response({'detail': 'You do not have permission to delete this post.'}, status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





from rest_framework import generics, permissions
from .models import ResearchPaper
from .serializers import ResearchPaperSerializer

# List all research papers (no authentication needed)
class ResearchPaperListView(generics.ListAPIView):
    queryset = ResearchPaper.objects.all()
    serializer_class = ResearchPaperSerializer

# Submit a new research paper (authentication required)
class ResearchPaperCreateView(generics.CreateAPIView):
    queryset = ResearchPaper.objects.all()
    serializer_class = ResearchPaperSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# Retrieve, update, or delete a specific research paper (author permission needed for update and delete)
class ResearchPaperDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResearchPaper.objects.all()
    serializer_class = ResearchPaperSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        return super().get_permissions()

# Custom permission to allow only authors to edit or delete their own research papers
from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


from .models import CRNotification
from .serializers import CRNotificationSerializer
from .permissions import IsStudentOrTeachers, IsCR

class CRNotificationListCreateAPIView(generics.ListCreateAPIView):
    queryset = CRNotification.objects.all()
    serializer_class = CRNotificationSerializer
    permission_classes = [IsStudentOrTeachers]  # Allow students and teachers to view notifications; only CRs can create

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'cr':
            return CRNotification.objects.all()  # CR can see all notifications
        elif user.user_type == 'student':
            return CRNotification.objects.filter(for_students=user) | CRNotification.objects.filter(for_students=None)
        elif user.user_type == 'teacher':
            return CRNotification.objects.filter(for_teachers=user) | CRNotification.objects.filter(for_teachers=None)
        return CRNotification.objects.none()

    def perform_create(self, serializer):
        # Ensure the user is a CR
        if self.request.user.user_type != 'cr':
            raise serializers.ValidationError("Only CRs can create notifications.")

        # Save the notification object with the CR as the creator
        notification = serializer.save(created_by=self.request.user)

        # Automatically select all students and associate them with the notification
        all_students = User.objects.filter(user_type='student')
        notification.for_students.set(all_students)

        # Optionally associate teachers with the notification
        teachers = serializer.validated_data.get('for_teachers', None)
        if teachers:
            notification.for_teachers.set(teachers)

        # Sending email to each student
        for student in all_students:
            subject = f"New CR Notification: {notification.title}"
            html_message = render_to_string('email/cr_notification_email.html', {'notification': notification})
            plain_message = strip_tags(html_message)
            from_email = 'mahmhdulabin@gmail.com'  # Replace with your actual email
            recipient_list = [student.email]

            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

        # Sending email to each teacher if they were included
        if teachers:
            for teacher in teachers:
                subject = f"New CR Notification: {notification.title}"
                html_message = render_to_string('email/cr_notification_email.html', {'notification': notification})
                plain_message = strip_tags(html_message)
                recipient_list = [teacher.email]

                send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

        # Save the notification after setting all recipients
        notification.save()

class crNotificationListView(generics.ListAPIView):
    queryset = CRNotification.objects.all()
    serializer_class = CRNotificationSerializer


from .models import CRNotification
from .serializers import CRNotificationSerializer

class CRDashboardAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access this view
    serializer_class = CRNotificationSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Ensure the user is a CR
        if user.user_type != 'cr':
            return Response({'error': 'Unauthorized access. Only Class Representatives (CRs) are allowed.'}, status=403)
        
        # Fetch all notifications created by the current CR
        cr_notifications = CRNotification.objects.filter(created_by=user)
        
        # Retrieve the total count of students and CRs
        total_students = CustomUser.objects.filter(user_type='student').count()
        total_crs = CustomUser.objects.filter(user_type='cr').count()
        # Serialize the notifications
        serializer = self.get_serializer(cr_notifications, many=True)
        
        # Return the serialized data in response
        return Response({
            'notification_count': cr_notifications.count(),
            'notifications': serializer.data,
            'total_students': total_students,
            'total_crs': total_crs,
        })

from users.models import CustomUser
class StudentCountView(APIView):
    def get(self, request, *args, **kwargs):
        student_count = CustomUser.objects.filter(user_type='student').count()
        return Response({'total_students': student_count}, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.response import Response
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from .models import Attendance, Course
from .serializers import AttendanceSerializer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch

class TakeAttendanceAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def post(self, request, *args, **kwargs):
        if request.user.user_type != 'cr':
            return Response({'error': 'Unauthorized access. Only Class Representatives (CRs) can take attendance.'}, status=403)

        course_id = request.data.get('course')
        date = request.data.get('date')

        if not course_id or not date:
            return Response({'error': 'Course and date are required.'}, status=400)

        course = get_object_or_404(Course, id=course_id)
        students = User.objects.filter(user_type='student')
        attendance_data = []

        for student in students:
            attendance_status = request.data.get(f'student_{student.id}')
            present = attendance_status == 'present' if attendance_status else False
            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=date,
                defaults={'present': present, 'cr': request.user}
            )
            # Append full name instead of username
            full_name = f"{student.first_name} {student.last_name}"
            attendance_data.append({
                'full_name': full_name,
                'present': 'Yes' if present else 'No'
            })

        pdf = self.generate_pdf(course, date, attendance_data)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="attendance_record.pdf"'
        return response



    def generate_pdf(self, course, date, attendance_data):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header for the PDF
        c.setFont("Helvetica-Bold", 18)
        c.drawString(100, height - 50, f'Attendance Record for {course.title}')
        
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 80, f'Date: {date}')
        c.drawString(100, height - 110, 'Student Attendance:')

        # Set up the table data with headers
        table_data = [['Student Name', 'Present']]

        # Populate the table with attendance data, using full names
        for entry in attendance_data:
            table_data.append([entry['full_name'], entry['present']])

        # Create a table with attendance data
        table = Table(table_data, colWidths=[3 * inch, 2 * inch])

        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)

        # Set the position for the table on the PDF
        table.wrapOn(c, width, height)
        table.drawOn(c, 100, height - 300)  # Adjust position as needed

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

