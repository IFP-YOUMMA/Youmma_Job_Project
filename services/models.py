from django.db import models 

class ServiceCategory(models.Model):

    """ Catégories de métiers (15 catégories prioritaires pour MVP) """ 
    name = models.CharField(max_length=100, unique=True) 
    slug = models.SlugField(max_length=100, unique=True) 
    description = models.TextField(blank=True) 
    icon = models.CharField( max_length=50, blank=True, help_text="Nom de l'icône (ex: wrench, hammer, etc.)" ) 
    is_active = models.BooleanField(default=True) 
    order = models.IntegerField(default=0, help_text="Ordre d'affichage") 
    created_at = models.DateTimeField(auto_now_add=True) 
    
    class Meta: 
        verbose_name = "Catégorie de service" 
        verbose_name_plural = "Catégories de services" 
        ordering = ['order', 'name'] 
        
    def __str__(self): return self.name