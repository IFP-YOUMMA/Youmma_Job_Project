from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required 
from django.contrib import messages 
from .models import ProviderProfile 
from .forms import ProviderProfileForm 
from .models import PortfolioImage
from django.http import HttpResponseForbidden
from .forms import PortfolioImageForm


@login_required 
def profile_create(request): 
    
    """Création du profil prestataire après inscription""" 
    if request.user.user_type != 'prestataire': 
        messages.error(request, 'Cette page est réservée aux prestataires.') 
        return redirect('/') 
    if hasattr(request.user, 'provider_profile'): 
        return redirect('profile_edit') 
    if request.method == 'POST': 
        form = ProviderProfileForm(request.POST, request.FILES) 
        if form.is_valid(): 
            profile = form.save(commit=False) 
            profile.user = request.user 
            profile.save() 
            messages.success(request, 'Profil créé avec succès !') 
            return redirect('profile_detail', pk=profile.pk) 
    else: 
        form = ProviderProfileForm() 
    return render(request, 'profiles/profile_form.html', {'form': form}) 

@login_required 
def profile_edit(request): 
    
    """Modification du profil prestataire""" 
    # Vérifier que l'utilisateur est un prestataire
    if request.user.user_type != 'prestataire':
        messages.error(request, 'Cette page est réservée aux prestataires.')
        return redirect('home')
    
    # Si le profil n'existe pas, rediriger vers la création
    if not hasattr(request.user, 'provider_profile'):
        messages.warning(request, 'Vous devez d\'abord créer votre profil.')
        return redirect('profiles:profile_create')
    
    profile = request.user.provider_profile
    if request.method == 'POST': 
        form = ProviderProfileForm(request.POST, request.FILES, instance=profile) 
        if form.is_valid(): 
            form.save() 
            messages.success(request, 'Profil mis à jour avec succès !') 
            return redirect('profiles:profile_detail', pk=profile.pk) 
    else: 
        form = ProviderProfileForm(instance=profile) 
    return render(request, 'profiles/profile_form.html', {'form': form}) 

def profile_detail(request, pk): 
    
    """Affichage détaillé d'un profil prestataire""" 
    profile = get_object_or_404(ProviderProfile, pk=pk) 
    reviews = profile.reviews.filter(is_verified=True).order_by('-created_at')[:5] 
    context = { 'profile': profile, 'reviews': reviews, } 
    return render(request, 'profiles/profile_detail.html', context)


@login_required
def my_profile(request):
    """
    Redirige vers le profil du prestataire connecté
    """
    if request.user.user_type != 'prestataire':
        messages.error(request, "Seuls les prestataires ont un profil public.")
        return redirect('home')
    
    if not hasattr(request.user, 'provider_profile'):
        messages.warning(request, "Vous devez d'abord créer votre profil.")
        return redirect('profiles:profile_create')
    
    return redirect('profiles:profile_detail', pk=request.user.provider_profile.pk)


@login_required
def portfolio_add(request):
    """
    Ajouter une image au portfolio
    """
    # Vérifier que l'utilisateur est un prestataire
    if request.user.user_type != 'prestataire':
        messages.error(request, "Cette page est réservée aux prestataires.")
        return redirect('home')
    
    # Vérifier que le profil existe
    if not hasattr(request.user, 'provider_profile'):
        messages.error(request, "Vous devez d'abord créer votre profil.")
        return redirect('profiles:profile_create')
    
    profile = request.user.provider_profile
    
    # Vérifier le nombre d'images (max 10)
    if profile.portfolio_images.count() >= 10:
        messages.error(request, "Vous avez atteint la limite de 10 images.")
        return redirect('profiles:profile_edit')
    
    if request.method == 'POST':
        form = PortfolioImageForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio_image = form.save(commit=False)
            portfolio_image.provider = profile
            portfolio_image.save()
            messages.success(request, "Image ajoutée à votre portfolio !")
            return redirect('profiles:profile_edit')
    else:
        form = PortfolioImageForm()
    
    return render(request, 'profiles/porfolio_add.html', {'form': form})


@login_required
def portfolio_delete(request, pk):
    """
    Supprimer une image du portfolio
    """
    image = get_object_or_404(PortfolioImage, pk=pk)
    
    # Vérifier que l'image appartient au prestataire connecté
    if image.provider.user != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette image.")
        return redirect('home')
    
    # Supprimer l'image
    image.delete()
    messages.success(request, "Image supprimée de votre portfolio.")
    return redirect('profiles:profile_edit')