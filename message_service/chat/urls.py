from django.urls import path
from .import views
urlpatterns = [
    path('h/',views.hello.as_view()),
    path("messages/", views.ChatHistoryView.as_view(), name="chat-history"),
    path("contact-list/", views.ContactListView.as_view()),
]
