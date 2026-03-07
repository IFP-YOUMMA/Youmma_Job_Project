from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Page d'acceuil'
    path('', views.home, name='home'),

    # Page de recherche principale
    path('search/', views.search_providers, name='search_providers'),
    
    # Recherche par catégorie spécifique
    path('category/<slug:category_slug>/', views.search_by_category, name='search_by_category'),
    
    # Recherche par ville
    path('city/<str:city>/', views.search_by_city, name='search_by_city'),
]