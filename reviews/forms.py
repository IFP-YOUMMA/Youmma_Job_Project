from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier un avis
    """
    
    # Choix de notation (1 à 5 étoiles)
    RATING_CHOICES = [
        (1, '⭐ 1 - Très insatisfait'),
        (2, '⭐⭐ 2 - Insatisfait'),
        (3, '⭐⭐⭐ 3 - Moyen'),
        (4, '⭐⭐⭐⭐ 4 - Satisfait'),
        (5, '⭐⭐⭐⭐⭐ 5 - Très satisfait'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'rating-radio'
        }),
        label='Votre note',
        required=True,
        help_text='Évaluez votre expérience avec ce prestataire'
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Partagez votre expérience avec ce prestataire. Décrivez la qualité du service, le professionnalisme, le respect des délais, etc.',
            'maxlength': 1000
        }),
        label='Votre commentaire',
        required=True,
        max_length=1000,
        help_text='Minimum 20 caractères, maximum 1000 caractères'
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
    
    def clean_comment(self):
        """Validation du commentaire"""
        comment = self.cleaned_data.get('comment')
        
        # Vérifier la longueur minimale
        if len(comment.strip()) < 20:
            raise forms.ValidationError(
                'Votre commentaire doit contenir au moins 20 caractères.'
            )
        
        # Vérifier que le commentaire n'est pas uniquement des espaces
        if not comment.strip():
            raise forms.ValidationError(
                'Votre commentaire ne peut pas être vide.'
            )
        
        return comment.strip()
    
    def clean_rating(self):
        """Validation de la note"""
        rating = self.cleaned_data.get('rating')
        
        # Convertir en entier
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            raise forms.ValidationError('Note invalide.')
        
        # Vérifier que la note est entre 1 et 5
        if rating < 1 or rating > 5:
            raise forms.ValidationError(
                'La note doit être comprise entre 1 et 5 étoiles.'
            )
        
        return rating