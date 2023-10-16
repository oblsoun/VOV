from django.urls import path
from . import views

app_name = 'realTimeDeidentificationApp'

urlpatterns=[
    path('', views.real_time, name='realTime'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('detect_image/', views.detect_image, name='detect_image'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('send_email/', views.send_email, name='send_email'),
    path('download/', views.download, name='download'),
    path('close/', views.close, name="close"),
]