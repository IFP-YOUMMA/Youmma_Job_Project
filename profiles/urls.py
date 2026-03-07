from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Création de profil (après inscription prestataire)
    path('create/', views.profile_create, name='profile_create'),
    
    # Modification de profil (prestataire connecté)
    path('edit/', views.profile_edit, name='profile_edit'),
    
    # Affichage détaillé d'un profil (public)
    path('<int:pk>/', views.profile_detail, name='profile_detail'),
    
    # Mon profil (redirection vers le profil du prestataire connecté)
    path('my-profile/', views.my_profile, name='my_profile'),
    
    # Gestion du portfolio
    path('portfolio/add/', views.portfolio_add, name='portfolio_add'),
    path('portfolio/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
]