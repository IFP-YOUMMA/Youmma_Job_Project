from django.db import models 
from django.conf import settings 
from services.models import ServiceCategory 


class ProviderProfile(models.Model): 
    
    """ Profil détaillé des prestataires de services """ 
    AVAILABILITY_CHOICES = ( ('available', 'Disponible'), ('busy', 'Occupé'), ('absent', 'Absent'), ) 
    user = models.OneToOneField( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile' ) 
    category = models.ForeignKey( ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='providers' ) 
    
    # Informations obligatoires 
    full_name = models.CharField(max_length=200) 
    profile_picture = models.ImageField( upload_to='profile_pics/', blank=True, null=True ) 
    city = models.CharField(max_length=100) 
    commune = models.CharField(max_length=100) 
    
    # Informations optionnelles 
    bio = models.TextField( blank=True, max_length=500, help_text="Description des services (max 500 caractères)" ) 
    years_experience = models.IntegerField( null=True, blank=True, help_text="Années d'expérience" ) 
    hourly_rate = models.DecimalField( max_digits=10, decimal_places=2, null=True, blank=True, help_text="Tarif horaire indicatif (GNF)" ) 
    availability = models.CharField( max_length=20, choices=AVAILABILITY_CHOICES, default='available' ) 
    
    # Vérification 
    is_verified = models.BooleanField(default=False) 
    identity_document = models.FileField( upload_to='identity_docs/', blank=True, null=True ) 
    
    # Statistiques 
    total_reviews = models.IntegerField(default=0) 
    average_rating = models.DecimalField( max_digits=3, decimal_places=2, default=0.00 ) 
    completed_jobs = models.IntegerField(default=0) 
    
    # Abonnement (Phase 2) 
    is_premium = models.BooleanField(default=False) 
    premium_until = models.DateField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta: 
        verbose_name = "Profil Prestataire" 
        verbose_name_plural = "Profils Prestataires" 
        ordering = ['-is_premium', '-average_rating', '-created_at'] 
        
        def __str__(self): return f"{self.full_name} - {self.category}"

class PortfolioImage(models.Model): 
    
    """ Images du portfolio du prestataire (max 10) """ 
    provider = models.ForeignKey( ProviderProfile, on_delete=models.CASCADE, related_name='portfolio_images' ) 
    image = models.ImageField(upload_to='portfolio/') 
    caption = models.CharField(max_length=200, blank=True) 
    order = models.IntegerField(default=0) 
    uploaded_at = models.DateTimeField(auto_now_add=True) 
    
    class Meta: 
        verbose_name = "Image Portfolio" 
        verbose_name_plural = "Images Portfolio" 
        ordering = ['order', '-uploaded_at'] 
        
    def __str__(self): return f"Portfolio - {self.provider.full_name}"