from django import forms 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser 


class ClientRegistrationForm(UserCreationForm): 
    
    """Formulaire d'inscription pour les clients""" 
    email = forms.EmailField(required=True) 
    phone_number = forms.CharField(max_length=20, required=True) 
    
    class Meta: 
        model = CustomUser 
        fields = ['username', 'email', 'phone_number', 'password1', 'password2'] 
        
    def save(self, commit=True): 
        user = super().save(commit=False) 
        user.user_type = 'client' 
        if commit: 
            user.save() 
        return user 

class ProviderRegistrationForm(UserCreationForm):
     
    """Formulaire d'inscription pour les prestataires""" 
    email = forms.EmailField(required=True) 
    phone_number = forms.CharField(max_length=20, required=True) 
    
    class Meta: 
        model = CustomUser 
        fields = ['username', 'email', 'phone_number', 'password1', 'password2'] 
        
    def save(self, commit=True): 
        user = super().save(commit=False) 
        user.user_type = 'prestataire' 
        if commit: 
            user.save() 
        return user

class LoginForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé
    Optionnel - Django auth suffit, mais permet plus de contrôle sur le design
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom d\'utilisateur ou email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'remember_me']


class PasswordResetRequestForm(forms.Form):
    """
    Formulaire pour demander une réinitialisation de mot de passe
    """
    email = forms.EmailField(
        label="Adresse email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'votre@email.com',
            'autofocus': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Aucun compte n'est associé à cette adresse email."
            )
        return email


class PasswordResetConfirmForm(forms.Form):
    """
    Formulaire pour définir un nouveau mot de passe après reset
    """
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nouveau mot de passe',
            'autofocus': True
        }),
        help_text="Minimum 8 caractères"
    )
    new_password2 = forms.CharField(
        label="Confirmer le mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmer le mot de passe'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    "Les deux mots de passe ne correspondent pas."
                )
            if len(password1) < 8:
                raise forms.ValidationError(
                    "Le mot de passe doit contenir au moins 8 caractères."
                )
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """
    Formulaire pour mettre à jour email et téléphone de l'utilisateur
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'votre@email.com'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '+224 XXX XXX XXX'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
        user_id = self.instance.id
        if CustomUser.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError(
                "Cette adresse email est déjà utilisée par un autre compte."
            )
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Vérifier que le numéro n'est pas déjà utilisé par un autre utilisateur
        user_id = self.instance.id
        if CustomUser.objects.exclude(id=user_id).filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "Ce numéro de téléphone est déjà utilisé par un autre compte."
            )
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        # Marquer email comme non vérifié si changé
        if 'email' in self.changed_data:
            user.email_verified = False
        # Marquer téléphone comme non vérifié si changé
        if 'phone_number' in self.changed_data:
            user.phone_verified = False
        
        if commit:
            user.save()
        return user