from django.urls import path
from . import views

app_name = 'fileDeidentificationApp'

urlpatterns=[
    path('send_email/', views.send_email, name='send_email'),
    path('download/', views.download, name='download'),
]