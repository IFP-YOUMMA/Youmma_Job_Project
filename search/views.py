from django.shortcuts import render 
from django.db.models import Q 
from profiles.models import ProviderProfile 
from services.models import ServiceCategory 


def home(request):
    """
    Vue de la page d'accueil avec statistiques et meilleurs prestataires
    """
    # Récupérer les 5 meilleurs prestataires (les mieux notés et vérifiés)
    top_providers = ProviderProfile.objects.filter(
        is_verified=True,
        average_rating__gt=0
    ).select_related('category', 'user').order_by('-average_rating', '-total_reviews')[:5]
    
    context = {
        'total_providers': ProviderProfile.objects.count(),
        'total_categories': ServiceCategory.objects.filter(is_active=True).count(),
        'featured_categories': ServiceCategory.objects.filter(is_active=True)[:6],
        'top_providers': top_providers,  # Ajout des meilleurs prestataires
    }
    return render(request, 'home_premium.html', context)

def search_providers(request): 
    
    """Recherche de prestataires avec filtres""" 
    providers = ProviderProfile.objects.all() 
    # Filtre par catégorie 
    category_slug = request.GET.get('category') 
    if category_slug: 
        providers = providers.filter(category__slug=category_slug) 
        
    # Filtre par ville  
    city = request.GET.get('city') 
    if city: 
        providers = providers.filter(city__icontains=city) 
    
    # Filtre par note 
    min_rating = request.GET.get('min_rating') 
    if min_rating: 
        providers = providers.filter(average_rating__gte=min_rating) 
    
    # Filtre par disponibilité 
    if request.GET.get('available_only'): 
        providers = providers.filter(availability='available') 
    
    # Recherche textuelle 
    query = request.GET.get('q') 
    if query: 
        providers = providers.filter( Q(full_name__icontains=query) | Q(bio__icontains=query) ) 
    
    # Tri 
    providers = providers.order_by('-is_premium', '-average_rating') 
    categories = ServiceCategory.objects.filter(is_active=True) 
    context = { 'providers': providers, 'categories': categories, 'selected_category': category_slug, 'selected_city': city, } 
    return render(request, 'search/search_results.html', context)


def search_by_category(request, category_slug):
    """Recherche de prestataires par catégorie spécifique"""
    providers = ProviderProfile.objects.filter(category__slug=category_slug)
    
    # Filtre par ville  
    city = request.GET.get('city') 
    if city: 
        providers = providers.filter(city__icontains=city) 
    
    # Filtre par note 
    min_rating = request.GET.get('min_rating') 
    if min_rating: 
        providers = providers.filter(average_rating__gte=min_rating) 
    
    # Filtre par disponibilité 
    if request.GET.get('available_only'): 
        providers = providers.filter(availability='available') 
    
    # Recherche textuelle 
    query = request.GET.get('q') 
    if query: 
        providers = providers.filter(Q(full_name__icontains=query) | Q(bio__icontains=query))
    
    # Tri 
    providers = providers.order_by('-is_premium', '-average_rating')
    categories = ServiceCategory.objects.filter(is_active=True)
    context = {
        'providers': providers,
        'categories': categories,
        'selected_category': category_slug,
        'selected_city': city,
    }
    return render(request, 'search/search_results.html', context)


def search_by_city(request, city):
    """Recherche de prestataires par ville spécifique"""
    providers = ProviderProfile.objects.filter(city__icontains=city)
    
    # Filtre par catégorie 
    category_slug = request.GET.get('category') 
    if category_slug: 
        providers = providers.filter(category__slug=category_slug) 
    
    # Filtre par note 
    min_rating = request.GET.get('min_rating') 
    if min_rating: 
        providers = providers.filter(average_rating__gte=min_rating) 
    
    # Filtre par disponibilité 
    if request.GET.get('available_only'): 
        providers = providers.filter(availability='available') 
    
    # Recherche textuelle 
    query = request.GET.get('q') 
    if query: 
        providers = providers.filter(Q(full_name__icontains=query) | Q(bio__icontains=query))
    
    # Tri 
    providers = providers.order_by('-is_premium', '-average_rating')
    categories = ServiceCategory.objects.filter(is_active=True)
    context = {
        'providers': providers,
        'categories': categories,
        'selected_category': category_slug,
        'selected_city': city,
    }
    return render(request, 'search/search_results.html', context)
