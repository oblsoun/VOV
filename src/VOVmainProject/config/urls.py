from django.contrib import admin
from django.urls import path, include
import fileDeidentificationApp.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', fileDeidentificationApp.views.file_upload, name='fileUpload'),
    path('fileUpload/', include('fileDeidentificationApp.urls')), 
    path('myphoto/', include('myPhotoApp.urls')),
    path('realTime/', include('realTimeDeidentificationApp.urls')),
    path('user/', include('userManagingApp.urls')),  
    path('accounts/', include('allauth.urls')),
]
