from django.urls import path
from .views import UserRegistrationAPIView, UserLogoutAPIView, activate, UserLoginApiView, UserListAPIView, UserDetailAPIView ,StudentDashboardAPIView,UserProfileAPIView

urlpatterns = [
    path('users/register', UserRegistrationAPIView.as_view(), name='register'),
    path('users/login', UserLoginApiView.as_view(), name='login'),
    path('users/logout', UserLogoutAPIView.as_view(), name='logout'),
    path('users/activate/<uid64>/<token>/', activate, name='activate'),
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('student/dashboard/', StudentDashboardAPIView.as_view(), name='student-dashboard'),
    # path('teacher/dashboard/', TeacherDashboardAPIView.as_view(), name='teacher-dashboard'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
]
