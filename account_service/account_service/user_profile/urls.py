
from django.urls import path
from .import views

urlpatterns = [
    path('profile/',views.UserProfileView.as_view()),
    path('self/',views.SelfUser.as_view()),
    path('profile-list/',views.AdminProfileListView.as_view()),
    path('admin-dashboard/',views.AdmindashBoard.as_view()),

]
