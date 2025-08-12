
from django.urls import path,include
from .import views

urlpatterns = [
    path('request-otp/',views.RequestOtpView.as_view()),
    path('verify-otp/',views.VerifyOtpView.as_view()),
    # path('o-authlogin/', include('allauth.urls')),
    path('google-login/', views.GoogleLoginAPIView.as_view(), name='google-login'),
    path('me/',views.selfUser.as_view()),

    path('self-profile/',views.selfProfile.as_view()),

    path('user-list/',views.AdminUserListView.as_view())
]
