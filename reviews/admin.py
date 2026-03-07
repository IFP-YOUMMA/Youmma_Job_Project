from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Administration des avis avec actions bulk et filtres avancés
    """
    
    # Colonnes affichées dans la liste
    list_display = [
        'client',
        'provider',
        'rating_display',
        'comment_preview',
        'is_verified',
        'is_flagged',
        'created_at'
    ]
    
    # Filtres dans la sidebar
    list_filter = [
        'rating',
        'is_verified',
        'is_flagged',
        'created_at',
        'provider__category',
        'provider__city',
    ]
    
    # Champs de recherche
    search_fields = [
        'client__username',
        'client__email',
        'provider__full_name',
        'provider__user__username',
        'comment',
    ]
    
    # Colonnes modifiables directement depuis la liste
    list_editable = [
        'is_verified',
    ]
    
    # Nombre d'éléments par page
    list_per_page = 50
    
    # Ordre par défaut (plus récents en premier)
    ordering = ['-created_at']
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations principales', {
            'fields': (
                'client',
                'provider',
                'rating',
            )
        }),
        ('Contenu', {
            'fields': (
                'comment',
            )
        }),
        ('Modération', {
            'fields': (
                'is_verified',
                'is_flagged',
            )
        }),
        ('Dates', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)  # Section repliable
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    # Actions personnalisées
    actions = [
        'approve_reviews',
        'disapprove_reviews',
        'flag_reviews',
        'unflag_reviews',
        'delete_flagged_reviews',
        'update_provider_stats',
    ]
    
    # === ACTIONS BULK ===
    
    @admin.action(description='✅ Approuver les avis sélectionnés')
    def approve_reviews(self, request, queryset):
        """Approuve les avis sélectionnés"""
        updated = queryset.update(is_verified=True)
        
        # Mettre à jour les stats de tous les prestataires concernés
        providers = set(queryset.values_list('provider', flat=True))
        for provider_id in providers:
            from profiles.models import ProviderProfile
            provider = ProviderProfile.objects.get(pk=provider_id)
            self._update_stats(provider)
        
        self.message_user(
            request,
            f'{updated} avis approuvé(s) avec succès. Statistiques mises à jour.'
        )
    
    @admin.action(description='❌ Désapprouver les avis sélectionnés')
    def disapprove_reviews(self, request, queryset):
        """Désapprouve les avis sélectionnés"""
        updated = queryset.update(is_verified=False)
        
        # Mettre à jour les stats de tous les prestataires concernés
        providers = set(queryset.values_list('provider', flat=True))
        for provider_id in providers:
            from profiles.models import ProviderProfile
            provider = ProviderProfile.objects.get(pk=provider_id)
            self._update_stats(provider)
        
        self.message_user(
            request,
            f'{updated} avis désapprouvé(s) avec succès. Statistiques mises à jour.'
        )
    
    @admin.action(description='🚩 Signaler les avis sélectionnés')
    def flag_reviews(self, request, queryset):
        """Marque les avis comme signalés"""
        updated = queryset.update(is_flagged=True)
        self.message_user(
            request,
            f'{updated} avis signalé(s) avec succès.'
        )
    
    @admin.action(description='✓ Retirer le signalement des avis')
    def unflag_reviews(self, request, queryset):
        """Retire le signalement des avis"""
        updated = queryset.update(is_flagged=False)
        self.message_user(
            request,
            f'{updated} avis dé-signalé(s) avec succès.'
        )
    
    @admin.action(description='🗑️ Supprimer les avis signalés')
    def delete_flagged_reviews(self, request, queryset):
        """Supprime uniquement les avis signalés parmi la sélection"""
        # Filtrer uniquement les avis signalés
        flagged_reviews = queryset.filter(is_flagged=True)
        count = flagged_reviews.count()
        
        if count == 0:
            self.message_user(
                request,
                "Aucun avis signalé dans la sélection.",
                level='warning'
            )
            return
        
        # Récupérer les prestataires avant suppression
        providers = set(flagged_reviews.values_list('provider', flat=True))
        
        # Supprimer les avis signalés
        flagged_reviews.delete()
        
        # Mettre à jour les stats
        for provider_id in providers:
            from profiles.models import ProviderProfile
            try:
                provider = ProviderProfile.objects.get(pk=provider_id)
                self._update_stats(provider)
            except ProviderProfile.DoesNotExist:
                pass
        
        self.message_user(
            request,
            f'{count} avis signalé(s) supprimé(s) avec succès. Statistiques mises à jour.'
        )
    
    @admin.action(description='🔄 Mettre à jour les statistiques des prestataires')
    def update_provider_stats(self, request, queryset):
        """Met à jour les statistiques de tous les prestataires concernés"""
        providers = set(queryset.values_list('provider', flat=True))
        
        for provider_id in providers:
            from profiles.models import ProviderProfile
            try:
                provider = ProviderProfile.objects.get(pk=provider_id)
                self._update_stats(provider)
            except ProviderProfile.DoesNotExist:
                pass
        
        self.message_user(
            request,
            f'Statistiques mises à jour pour {len(providers)} prestataire(s).'
        )
    
    # === MÉTHODES HELPER ===
    
    def _update_stats(self, provider):
        """Met à jour les statistiques d'un prestataire"""
        from django.db.models import Avg, Count
        
        stats = Review.objects.filter(
            provider=provider,
            is_verified=True
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        provider.average_rating = round(stats['avg_rating'] or 0, 1)
        provider.total_reviews = stats['total_reviews'] or 0
        provider.save(update_fields=['average_rating', 'total_reviews'])
    
    # === MÉTHODES D'AFFICHAGE PERSONNALISÉES ===
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        qs = super().get_queryset(request)
        return qs.select_related('client', 'provider', 'provider__user')
    
    def rating_display(self, obj):
        """Affiche la note avec des étoiles"""
        stars = '⭐' * obj.rating
        return f'{stars} ({obj.rating}/5)'
    rating_display.short_description = 'Note'
    rating_display.admin_order_field = 'rating'
    
    def comment_preview(self, obj):
        """Affiche un aperçu du commentaire"""
        if len(obj.comment) > 100:
            return f'{obj.comment[:100]}...'
        return obj.comment
    comment_preview.short_description = 'Commentaire'
    
    def is_verified(self, obj):
        """Affiche une icône pour l'approbation"""
        return '✅' if obj.is_verified else '❌'
    is_verified.short_description = 'Approuvé'
    is_verified.admin_order_field = 'is_verified'
    
    def is_flagged(self, obj):
        """Affiche une icône pour le signalement"""
        return '🚩' if obj.is_flagged else '—'
    is_flagged.short_description = 'Signalé'
    is_flagged.admin_order_field = 'is_flagged'