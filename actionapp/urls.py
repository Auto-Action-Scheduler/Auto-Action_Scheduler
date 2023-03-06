from django.urls import path
from .views import (ActionCreateListAPIView, ActionRetrieveUpdateDestroyAPIView, CancelActionAPIView,
                    CreateReminderAPIView, UserCreateListAPIView)

urlpatterns = [
    path('create-list', ActionCreateListAPIView.as_view(), name='create-list'),
    path('retrieve-update-destroy/<int:pk>', ActionRetrieveUpdateDestroyAPIView.as_view(),
         name='retrieve-update-destroy'),
    path('cancel-action', CancelActionAPIView.as_view(), name='cancel-action'),
    path('create-reminder', CreateReminderAPIView.as_view(), name='create-reminder'),
    path('create-list-user', UserCreateListAPIView.as_view(), name='create-list-user'),
    # path('message-retrieve-update-destroy/<int:pk>', MessageRetrieveUpdateDestroyAPIView.as_view(),
    #      name='message-create-list'),
    # path('reminder-create-list', ReminderCreateListAPIView.as_view(), name='reminder-create-list'),
    # path('reminder-retrieve-update-destroy/<int:pk>', ReminderRetrieveUpdateDestroyAPIView.as_view(),
    #      name='reminder-retrieve-update-destroy'),
]
