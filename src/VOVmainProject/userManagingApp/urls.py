from django.urls import path
from . import views

app_name = 'userManagingApp'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.sign_up, name='signup'),
    path('check_userid/', views.id_overlap_check, name='check_userid'),
    path('send_email/', views.send_email, name='send_email'),
    path('check_code/', views.check_code, name='check_code'),
    path('read/',views.show_mypage, name='myPage'),
]