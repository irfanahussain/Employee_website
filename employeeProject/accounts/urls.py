from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('redirect/',views.redirect_dashboard,name='redirect_dashboard'),
    path('password-change/',views.CustomPasswordChangeView.as_view(),name='password_change'),
    path('password-change/done/',views.password_change_done,name='password_change_done'),
    path('profile/',views.profile_view,name='profile'),
]
