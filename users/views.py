from django.shortcuts import render, redirect 
from django.contrib.auth import login 
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .forms import (
    ClientRegistrationForm, 
    ProviderRegistrationForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
    ProfileUpdateForm
)
from .models import CustomUser


def register_client(request):
    """Inscription pour les clients"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie ! Bienvenue sur YOUMMA-JOB.')
            return redirect('home')
    else:
        form = ClientRegistrationForm()
    return render(request, 'users/register_client.html', {'form': form})


def register_provider(request):
    """Inscription pour les prestataires"""
    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie ! Complétez maintenant votre profil.')
            return redirect('profiles:profile_create')
    else:
        form = ProviderRegistrationForm()
    return render(request, 'users/register_provider.html', {'form': form})


def password_reset_request(request):
    """
    Vue pour demander une réinitialisation de mot de passe
    Envoie un email avec un lien de réinitialisation
    """
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            
            # Générer le token de réinitialisation
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Créer l'URL de réinitialisation
            reset_url = request.build_absolute_uri(
                f'/users/password-reset-confirm/{uid}/{token}/'
            )
            
            # Préparer l'email
            subject = 'Réinitialisation de votre mot de passe YOUMMA-JOB'
            message = render_to_string('users/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            
            # Envoyer l'email
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(
                    request, 
                    'Un email de réinitialisation a été envoyé à votre adresse.'
                )
                return redirect('login')
            except Exception as e:
                messages.error(
                    request, 
                    'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.'
                )
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    """
    Vue pour confirmer la réinitialisation et définir un nouveau mot de passe
    """
    try:
        # Décoder l'ID utilisateur
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    # Vérifier que le token est valide
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                # Définir le nouveau mot de passe
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                
                messages.success(
                    request, 
                    'Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.'
                )
                return redirect('login')
        else:
            form = PasswordResetConfirmForm()
        
        return render(request, 'users/password_reset_confirm.html', {
            'form': form,
            'validlink': True
        })
    else:
        # Lien invalide ou expiré
        messages.error(
            request, 
            'Le lien de réinitialisation est invalide ou a expiré.'
        )
        return render(request, 'users/password_reset_confirm.html', {
            'validlink': False
        })


@login_required
def profile_update(request):
    """
    Vue pour mettre à jour l'email et le numéro de téléphone de l'utilisateur
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Messages d'information si email ou téléphone changé
            if 'email' in form.changed_data:
                messages.warning(
                    request,
                    'Votre email a été modifié. Veuillez le vérifier pour continuer à utiliser toutes les fonctionnalités.'
                )
            if 'phone_number' in form.changed_data:
                messages.warning(
                    request,
                    'Votre numéro de téléphone a été modifié. Veuillez le vérifier pour continuer à utiliser toutes les fonctionnalités.'
                )
            
            if not form.changed_data:
                messages.info(request, 'Aucune modification effectuée.')
            else:
                messages.success(request, 'Vos informations ont été mises à jour avec succès.')
            
            # Rediriger selon le type d'utilisateur
            if request.user.user_type == 'prestataire':
                return redirect('profiles:my_profile')
            else:
                return redirect('home')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'users/profile_update.html', {
        'form': form
    })