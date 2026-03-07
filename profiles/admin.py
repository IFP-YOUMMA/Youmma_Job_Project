from django.contrib import admin
from .models import ProviderProfile, PortfolioImage


class PortfolioImageInline(admin.TabularInline):
    """
    Affichage des images du portfolio en ligne dans le profil
    """
    model = PortfolioImage
    extra = 1
    max_num = 10
    fields = ['image', 'caption', 'order', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    """
    Administration des profils prestataires avec actions bulk
    """
    
    # Colonnes affichées dans la liste
    list_display = [
        'full_name',
        'user',
        'category',
        'city',
        'is_verified',
        'is_premium',
        'average_rating',
        'total_reviews',
        'completed_jobs',
        'availability',
        'created_at'
    ]
    
    # Filtres dans la sidebar
    list_filter = [
        'category',
        'city',
        'is_verified',
        'is_premium',
        'availability',
        'created_at',
        'updated_at',
    ]
    
    # Champs de recherche
    search_fields = [
        'full_name',
        'user__username',
        'user__email',
        'user__phone_number',
        'bio',
        'city',
        'commune'
    ]
    
    # Colonnes modifiables directement depuis la liste
    list_editable = [
        'is_verified',
        'is_premium',
        'availability'
    ]
    
    # Nombre d'éléments par page
    list_per_page = 50
    
    # Ordre par défaut
    ordering = ['-is_premium', '-average_rating', '-created_at']
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations de base', {
            'fields': (
                'user',
                'full_name',
                'category',
                'profile_picture',
            )
        }),
        ('Localisation', {
            'fields': (
                'city',
                'commune',
            )
        }),
        ('Détails professionnels', {
            'fields': (
                'bio',
                'years_experience',
                'hourly_rate',
                'availability',
            )
        }),
        ('Vérification et Premium', {
            'fields': (
                'is_verified',
                'identity_document',
                'is_premium',
                'premium_until',
            )
        }),
        ('Statistiques', {
            'fields': (
                'total_reviews',
                'average_rating',
                'completed_jobs',
            ),
            'classes': ('collapse',)  # Section repliable
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
        'total_reviews',
        'average_rating',
        'completed_jobs',
        'created_at',
        'updated_at'
    ]
    
    # Afficher les images du portfolio en ligne
    inlines = [PortfolioImageInline]
    
    # Actions personnalisées
    actions = [
        'verify_profiles',
        'unverify_profiles',
        'activate_premium',
        'deactivate_premium',
        'set_available',
        'set_busy',
        'set_absent',
    ]
    
    # === ACTIONS BULK ===
    
    @admin.action(description='✅ Vérifier les profils sélectionnés')
    def verify_profiles(self, request, queryset):
        """Vérifie les profils sélectionnés"""
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            f'{updated} profil(s) vérifié(s) avec succès.'
        )
    
    @admin.action(description='❌ Dévérifier les profils sélectionnés')
    def unverify_profiles(self, request, queryset):
        """Retire la vérification des profils sélectionnés"""
        updated = queryset.update(is_verified=False)
        self.message_user(
            request,
            f'{updated} profil(s) dévérifié(s) avec succès.'
        )
    
    @admin.action(description='⭐ Activer Premium')
    def activate_premium(self, request, queryset):
        """Active le statut Premium pour les profils sélectionnés"""
        from datetime import date, timedelta
        
        # Définir la date d'expiration à 30 jours
        premium_until = date.today() + timedelta(days=30)
        
        updated = queryset.update(
            is_premium=True,
            premium_until=premium_until
        )
        
        self.message_user(
            request,
            f'{updated} profil(s) passé(s) en Premium (expire le {premium_until.strftime("%d/%m/%Y")}).'
        )
    
    @admin.action(description='💎 Désactiver Premium')
    def deactivate_premium(self, request, queryset):
        """Désactive le statut Premium"""
        updated = queryset.update(
            is_premium=False,
            premium_until=None
        )
        
        self.message_user(
            request,
            f'{updated} profil(s) retiré(s) du Premium.'
        )
    
    @admin.action(description='🟢 Marquer comme Disponible')
    def set_available(self, request, queryset):
        """Marque les profils comme disponibles"""
        updated = queryset.update(availability='available')
        self.message_user(
            request,
            f'{updated} profil(s) marqué(s) comme disponible(s).'
        )
    
    @admin.action(description='🟡 Marquer comme Occupé')
    def set_busy(self, request, queryset):
        """Marque les profils comme occupés"""
        updated = queryset.update(availability='busy')
        self.message_user(
            request,
            f'{updated} profil(s) marqué(s) comme occupé(s).'
        )
    
    @admin.action(description='🔴 Marquer comme Absent')
    def set_absent(self, request, queryset):
        """Marque les profils comme absents"""
        updated = queryset.update(availability='absent')
        self.message_user(
            request,
            f'{updated} profil(s) marqué(s) comme absent(s).'
        )
    
    # === MÉTHODES D'AFFICHAGE PERSONNALISÉES ===
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category').prefetch_related('portfolio_images')
    
    # Personnalisation de l'affichage
    def is_verified(self, obj):
        """Affiche une icône pour la vérification"""
        return '✅' if obj.is_verified else '❌'
    is_verified.short_description = 'Vérifié'
    is_verified.admin_order_field = 'is_verified'
    
    def is_premium(self, obj):
        """Affiche une icône pour le statut Premium"""
        return '⭐' if obj.is_premium else '—'
    is_premium.short_description = 'Premium'
    is_premium.admin_order_field = 'is_premium'
    
    def average_rating(self, obj):
        """Affiche la note moyenne avec des étoiles"""
        if obj.average_rating > 0:
            return f'⭐ {obj.average_rating:.1f}/5'
        return '—'
    average_rating.short_description = 'Note moyenne'
    average_rating.admin_order_field = 'average_rating'


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    """
    Administration des images du portfolio
    Liste personnalisée avec aperçu des images
    """
    
    # Colonnes affichées
    list_display = [
        'image_preview',
        'provider',
        'caption',
        'order',
        'uploaded_at'
    ]
    
    # Filtres
    list_filter = [
        'uploaded_at',
        'provider__category',
        'provider__city',
    ]
    
    # Recherche
    search_fields = [
        'provider__full_name',
        'caption',
    ]
    
    # Colonnes modifiables
    list_editable = [
        'caption',
        'order'
    ]
    
    # Ordre par défaut
    ordering = ['-uploaded_at']
    
    # Nombre d'éléments par page
    list_per_page = 50
    
    # Organisation des champs
    fields = [
        'provider',
        'image',
        'image_preview_large',
        'caption',
        'order',
        'uploaded_at'
    ]
    
    # Champs en lecture seule
    readonly_fields = [
        'uploaded_at',
        'image_preview_large'
    ]
    
    # Actions
    actions = [
        'move_to_first',
        'move_to_last',
    ]
    
    # === MÉTHODES D'AFFICHAGE PERSONNALISÉES ===
    
    def image_preview(self, obj):
        """Affiche un aperçu miniature de l'image"""
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px;" />'
        return '—'
    image_preview.short_description = 'Aperçu'
    image_preview.allow_tags = True
    
    def image_preview_large(self, obj):
        """Affiche un aperçu plus grand dans le formulaire"""
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 500px; max-height: 500px; object-fit: contain; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />'
        return '—'
    image_preview_large.short_description = 'Aperçu de l\'image'
    image_preview_large.allow_tags = True
    
    # === ACTIONS BULK ===
    
    @admin.action(description='⬆️ Déplacer en premier (order = 0)')
    def move_to_first(self, request, queryset):
        """Met les images sélectionnées en première position"""
        updated = queryset.update(order=0)
        self.message_user(
            request,
            f'{updated} image(s) déplacée(s) en première position.'
        )
    
    @admin.action(description='⬇️ Déplacer en dernier (order = 999)')
    def move_to_last(self, request, queryset):
        """Met les images sélectionnées en dernière position"""
        updated = queryset.update(order=999)
        self.message_user(
            request,
            f'{updated} image(s) déplacée(s) en dernière position.'
        )
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        qs = super().get_queryset(request)
        return qs.select_related('provider', 'provider__user')