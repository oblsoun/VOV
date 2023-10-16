from django.urls import path
from . import views

app_name = 'myPhotoApp'

urlpatterns = [
    path('', views.my_photo_list_up, name='myphoto'),
    path('imageprocess/',views.my_photo_button, name='button'),
    path('download/', views.my_photo_save, name='download'),
    path('delete/', views.my_photo_delete, name='delete'),
]

