from django.contrib.auth.models import AbstractUser 
from django.db import models


class CustomUser(AbstractUser):
     
    """ Modèle utilisateur personnalisé avec distinction client/prestataire """ 
    USER_TYPE_CHOICES = ( 
        ('client', 'Client'), 
        ('prestataire', 'Prestataire'), 
    ) 
    user_type = models.CharField( max_length=20, choices=USER_TYPE_CHOICES, default='client' ) 
    phone_number = models.CharField( max_length=20, unique=True, help_text="Numéro de téléphone (format: +224XXXXXXXXX)" ) 
    phone_verified = models.BooleanField(default=False) 
    email_verified = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta: 
        verbose_name = "Utilisateur" 
        verbose_name_plural = "Utilisateurs" 
        
    def __str__(self): return f"{self.username} ({self.get_user_type_display()})"

