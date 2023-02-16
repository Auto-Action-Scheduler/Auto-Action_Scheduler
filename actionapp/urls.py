from django.urls import path
from .views import (MailCreateListAPIView, MailRetrieveUpdateDestroyAPIView, MessageCreateListAPIView,
                    MessageRetrieveUpdateDestroyAPIView, ReminderCreateListAPIView,
                    ReminderRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('mail-create-list', MailCreateListAPIView.as_view(), name='mail-create-list'),
    path('mail-retrieve-update-destroy/<int:pk>', MailRetrieveUpdateDestroyAPIView.as_view(),
         name='mail-retrieve-update-destroy'),
    path('message-create-list', MessageCreateListAPIView.as_view(), name='message-create-list'),
    path('message-retrieve-update-destroy/<int:pk>', MessageRetrieveUpdateDestroyAPIView.as_view(),
         name='message-create-list'),
    path('reminder-create-list', ReminderCreateListAPIView.as_view(), name='reminder-create-list'),
    path('reminder-retrieve-update-destroy/<int:pk>', ReminderRetrieveUpdateDestroyAPIView.as_view(),
         name='reminder-retrieve-update-destroy'),
]
