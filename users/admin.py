from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administration personnalisée pour le modèle CustomUser
    avec actions bulk et filtres avancés
    """
    
    # Colonnes affichées dans la liste
    list_display = [
        'username', 
        'email', 
        'phone_number', 
        'user_type', 
        'phone_verified',
        'email_verified',
        'is_active',
        'date_joined'
    ]
    
    # Filtres dans la sidebar
    list_filter = [
        'user_type',           # Filtre par type (client/prestataire)
        'phone_verified',      # Filtre par téléphone vérifié
        'email_verified',      # Filtre par email vérifié
        'is_active',           # Filtre par actif/inactif
        'is_staff',            # Filtre par staff
        'is_superuser',        # Filtre par superuser
        'date_joined',         # Filtre par date d'inscription
        'last_login',          # Filtre par dernière connexion
    ]
    
    # Champs de recherche
    search_fields = [
        'username', 
        'email', 
        'phone_number',
        'first_name',
        'last_name'
    ]
    
    # Colonnes modifiables directement depuis la liste
    list_editable = [
        'is_active',
    ]
    
    # Nombre d'éléments par page
    list_per_page = 50
    
    # Ordre par défaut (plus récents en premier)
    ordering = ['-date_joined']
    
    # Organisation des champs dans le formulaire de détail
    fieldsets = UserAdmin.fieldsets + (
        ('Informations YOUMMA-JOB', {
            'fields': (
                'user_type', 
                'phone_number', 
                'phone_verified', 
                'email_verified'
            )
        }),
    )
    
    # Champs affichés lors de la création d'un utilisateur
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': (
                'user_type',
                'phone_number',
                'email',
            )
        }),
    )
    
    # Actions personnalisées
    actions = [
        'activate_users',
        'deactivate_users',
        'verify_phone',
        'unverify_phone',
        'verify_email',
        'unverify_email',
        'make_provider',
        'make_client',
    ]
    
    # === ACTIONS BULK ===
    
    @admin.action(description='✅ Activer les utilisateurs sélectionnés')
    def activate_users(self, request, queryset):
        """Active les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} utilisateur(s) activé(s) avec succès.'
        )
    
    @admin.action(description='❌ Désactiver les utilisateurs sélectionnés')
    def deactivate_users(self, request, queryset):
        """Désactive les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} utilisateur(s) désactivé(s) avec succès.'
        )
    
    @admin.action(description='📱 Vérifier les téléphones')
    def verify_phone(self, request, queryset):
        """Marque les téléphones comme vérifiés"""
        updated = queryset.update(phone_verified=True)
        self.message_user(
            request,
            f'{updated} téléphone(s) vérifié(s) avec succès.'
        )
    
    @admin.action(description='📱 Dévérifier les téléphones')
    def unverify_phone(self, request, queryset):
        """Marque les téléphones comme non vérifiés"""
        updated = queryset.update(phone_verified=False)
        self.message_user(
            request,
            f'{updated} téléphone(s) dévérifié(s) avec succès.'
        )
    
    @admin.action(description='📧 Vérifier les emails')
    def verify_email(self, request, queryset):
        """Marque les emails comme vérifiés"""
        updated = queryset.update(email_verified=True)
        self.message_user(
            request,
            f'{updated} email(s) vérifié(s) avec succès.'
        )
    
    @admin.action(description='📧 Dévérifier les emails')
    def unverify_email(self, request, queryset):
        """Marque les emails comme non vérifiés"""
        updated = queryset.update(email_verified=False)
        self.message_user(
            request,
            f'{updated} email(s) dévérifié(s) avec succès.'
        )
    
    @admin.action(description='👷 Convertir en Prestataire')
    def make_provider(self, request, queryset):
        """Convertit les utilisateurs en prestataires"""
        updated = queryset.update(user_type='prestataire')
        self.message_user(
            request,
            f'{updated} utilisateur(s) converti(s) en prestataire(s).'
        )
    
    @admin.action(description='👤 Convertir en Client')
    def make_client(self, request, queryset):
        """Convertit les utilisateurs en clients"""
        updated = queryset.update(user_type='client')
        self.message_user(
            request,
            f'{updated} utilisateur(s) converti(s) en client(s).'
        )
    
    # === MÉTHODES D'AFFICHAGE PERSONNALISÉES ===
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        qs = super().get_queryset(request)
        return qs.select_related()
    
    # Personnalisation de l'affichage
    def phone_verified(self, obj):
        """Affiche une icône pour phone_verified"""
        return '✅' if obj.phone_verified else '❌'
    phone_verified.short_description = 'Tél. vérifié'
    
    def email_verified(self, obj):
        """Affiche une icône pour email_verified"""
        return '✅' if obj.email_verified else '❌'
    email_verified.short_description = 'Email vérifié'