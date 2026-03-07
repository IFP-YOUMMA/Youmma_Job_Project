from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Review
from .forms import ReviewForm
from profiles.models import ProviderProfile


def update_provider_stats(provider):
    """
    Fonction helper pour mettre à jour les statistiques d'un prestataire
    (note moyenne et nombre total d'avis)
    """
    # Calculer les statistiques à partir des avis approuvés
    stats = Review.objects.filter(
        provider=provider,
        is_approved=True
    ).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Mettre à jour le profil
    provider.average_rating = round(stats['avg_rating'] or 0, 1)
    provider.total_reviews = stats['total_reviews'] or 0
    provider.save(update_fields=['average_rating', 'total_reviews'])


@login_required
def create_review(request, provider_id):
    """
    Créer un avis pour un prestataire
    """
    # Récupérer le profil du prestataire
    provider = get_object_or_404(ProviderProfile, pk=provider_id)
    
    # Vérifier que l'utilisateur est un client
    if request.user.user_type != 'client':
        messages.error(request, "Seuls les clients peuvent laisser des avis.")
        return redirect('profiles:profile_detail', pk=provider_id)
    
    # Vérifier que le client n'a pas déjà laissé un avis pour ce prestataire
    existing_review = Review.objects.filter(
        client=request.user,
        provider=provider
    ).first()
    
    if existing_review:
        messages.warning(
            request,
            "Vous avez déjà laissé un avis pour ce prestataire. Vous pouvez le modifier."
        )
        return redirect('reviews:edit_review', pk=existing_review.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user
            review.provider = provider
            review.save()
            
            # Mettre à jour les statistiques du prestataire
            update_provider_stats(provider)
            
            messages.success(
                request,
                "Votre avis a été publié avec succès. Merci pour votre retour !"
            )
            return redirect('profiles:profile_detail', pk=provider_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'provider': provider,
    }
    return render(request, 'reviews/create_review.html', context)


@login_required
def edit_review(request, pk):
    """
    Modifier un avis existant
    """
    review = get_object_or_404(Review, pk=pk)
    
    # Vérifier que l'utilisateur est l'auteur de l'avis
    if review.client != request.user:
        messages.error(request, "Vous ne pouvez pas modifier cet avis.")
        return redirect('home')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            
            # Mettre à jour les statistiques du prestataire
            update_provider_stats(review.provider)
            
            messages.success(request, "Votre avis a été modifié avec succès.")
            return redirect('profiles:profile_detail', pk=review.provider.pk)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'provider': review.provider,
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
def delete_review(request, pk):
    """
    Supprimer un avis
    """
    review = get_object_or_404(Review, pk=pk)
    
    # Vérifier que l'utilisateur est l'auteur
    if review.client != request.user:
        messages.error(request, "Vous ne pouvez pas supprimer cet avis.")
        return redirect('home')
    
    provider = review.provider
    review.delete()
    
    # Mettre à jour les statistiques
    update_provider_stats(provider)
    
    messages.success(request, "Votre avis a été supprimé.")
    return redirect('profiles:profile_detail', pk=provider.pk)


@login_required
def flag_review(request, pk):
    """
    Signaler un avis comme abusif
    """
    review = get_object_or_404(Review, pk=pk)
    
    # Vérifier que l'utilisateur n'est pas l'auteur de l'avis
    if review.client == request.user:
        messages.error(request, "Vous ne pouvez pas signaler votre propre avis.")
        return redirect('profiles:profile_detail', pk=review.provider.pk)
    
    # Marquer l'avis comme signalé
    if not review.is_flagged:
        review.is_flagged = True
        review.save(update_fields=['is_flagged'])
        messages.success(
            request,
            "L'avis a été signalé. Notre équipe va l'examiner."
        )
    else:
        messages.info(request, "Cet avis a déjà été signalé.")
    
    return redirect('profiles:profile_detail', pk=review.provider.pk)