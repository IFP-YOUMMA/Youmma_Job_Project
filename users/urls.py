from django.urls import path 
from django.contrib.auth import views as auth_views 
from . import views 

urlpatterns = [
     
    path('register/client/', views.register_client, name='register_client'), 
    path('register/provider/', views.register_provider, name='register_provider'), 
    path('login/', auth_views.LoginView.as_view(
        template_name='users/register_client.html',
        redirect_authenticated_user=True
    ), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),

]