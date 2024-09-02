from django.urls import path
from .views import CourseListCreateAPIView, EnrollmentListCreateAPIView, AssignmentListCreateAPIView, NotificationListCreateAPIView,NotificationDetailAPIView,AssignmentDetailUpdateAPIView,NotificationSearchAPIView,AssignmentSearchAPIView,AssignmentSearchByCourseAPIView,SubmitAssignmentAPIView,TeacherDashboardAPIView,SubmitAssignmentView,CourseDetailAPIView,BlogPostList,BlogPostDetail,ResearchPaperCreateView,ResearchPaperDetailView,ResearchPaperListView,CRNotificationListCreateAPIView,crNotificationListView,CRDashboardAPIView,StudentCountView,TakeAttendanceAPIView

urlpatterns = [
    path('courses/', CourseListCreateAPIView.as_view(), name='course-list-create'),
    path('enrollments/', EnrollmentListCreateAPIView.as_view(), name='enrollment-list-create'),
    path('assignments/', AssignmentListCreateAPIView.as_view(), name='assignment-list-create'),
    path('notifications/', NotificationListCreateAPIView.as_view(), name='notification-list-create'),
    path('notifications/<int:pk>/', NotificationDetailAPIView.as_view(), name='notification-detail'),
    path('assignments/<int:pk>/', AssignmentDetailUpdateAPIView.as_view(), name='assignment-detail-update'),
    path('notifications/search/<str:course_code>/', NotificationSearchAPIView.as_view(), name='notification-search'),
    # path('assignments/search/', AssignmentSearchAPIView.as_view(), name='assignment-search'),
    path('assignments/search/<str:search_param>/', AssignmentSearchByCourseAPIView.as_view(), name='assignment-search-by-course'),
    path('assignments/submit/', SubmitAssignmentAPIView.as_view(), name='submit-assignment'),
    path('teacher/dashboard/', TeacherDashboardAPIView.as_view(), name='teacher-dashboard'),
    path('submit-assignment/', SubmitAssignmentView.as_view(), name='submit-assignment'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('blog/', BlogPostList.as_view(), name='blog-post-list'),
    path('blog/<int:pk>/', BlogPostDetail.as_view(), name='blog-post-detail'),
    path('papers/', ResearchPaperListView.as_view(), name='paper-list'),
    path('papers/submit/', ResearchPaperCreateView.as_view(), name='paper-submit'),
    path('papers/<int:pk>/', ResearchPaperDetailView.as_view(), name='paper-detail'),
    path('cr', CRNotificationListCreateAPIView.as_view(), name='cr-notification-list-create'),
    path('crlist', crNotificationListView.as_view(), name='cr-list-create'),
    path('cr/dashboard/', CRDashboardAPIView.as_view(), name='cr-dashboard'),
    path('stdn/', StudentCountView.as_view(), name='student_count'),
    path('attendance/', TakeAttendanceAPIView.as_view(), name='take_attendance'),
]
