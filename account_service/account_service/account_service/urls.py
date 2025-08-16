
from django.contrib import admin
from django.urls import path,include
from user_account.views import GitHubLoginAPIView

from django.urls import path
from django.http import JsonResponse

def home(request):
    return JsonResponse({"status": "Account service is running"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',include('user_account.urls')),
    path('user/',include('user_profile.urls')),
    # path('accounts/',include('allauth.urls')),

    # path('auth/', include('dj_rest_auth.urls')),  # login/logout/password reset
    # path('auth/registration/', include('dj_rest_auth.registration.urls')),  # registration

    # OAuth endpoints (e.g., Google)
    # path('auth/oauth/', include('allauth.urls')),  # needed for Google login



    # path('auth/', include('dj_rest_auth.urls')),
    # path('auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('auth/', include('allauth.socialaccount.urls')),

    path('auth/social/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('auth/social/login', include('allauth.socialaccount.urls'),name='social_login'),
    path("auth/github/", GitHubLoginAPIView.as_view()),

]

urlpatterns += [
    path('', home),  # this is just http://service/
]
