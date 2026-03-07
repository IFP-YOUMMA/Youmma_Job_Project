from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Créer un avis pour un prestataire
    path('create/<int:provider_id>/', views.create_review, name='create_review'),
    
    # Modifier un avis (optionnel - si vous voulez permettre la modification)
    path('edit/<int:pk>/', views.edit_review, name='edit_review'),
    
    # Supprimer un avis (optionnel)
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),
    
    # Signaler un avis comme abusif
    path('flag/<int:pk>/', views.flag_review, name='flag_review'),
]