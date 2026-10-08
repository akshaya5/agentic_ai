
from django.urls import path
from . import views

urlpatterns = [
    path("chat/<int:id>/", views.chat, name ="chat"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/<int:pk>/", views.conversation_detail, name="conversation_detail"),
    path("dashboard/stream/<int:conversation_id>/", views.conversation_stream, name="conversation_stream")
]