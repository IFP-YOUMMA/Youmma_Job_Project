from django.db import models 
from django.conf import settings 
from django.core.validators import MinValueValidator, MaxValueValidator 
from profiles.models import ProviderProfile 


class Review(models.Model): 
    
    """ Avis et notes des clients sur les prestataires """ 
    provider = models.ForeignKey( ProviderProfile, on_delete=models.CASCADE, related_name='reviews' ) 
    client = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given' ) 
    rating = models.IntegerField( validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Note de 1 à 5 étoiles" ) 
    comment = models.TextField(help_text="Commentaire obligatoire") 
    is_verified = models.BooleanField( default=False, help_text="Avis vérifié par l'admin" ) 
    is_flagged = models.BooleanField( default=False, help_text="Signalé comme abusif" ) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta: 
        verbose_name = "Avis" 
        verbose_name_plural = "Avis" 
        ordering = ['-created_at'] 
        unique_together = ['provider', 'client'] 
        
    # Un client = un avis par prestataire 
    def __str__(self): return f"{self.client.username} → {self.provider.full_name} ({self.rating}★)"