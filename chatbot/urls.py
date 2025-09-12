from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/', views.ChatBotView.as_view(), name='chatbot_api'),
    path('widget/', views.chatbot_widget, name='chatbot_widget'),
]