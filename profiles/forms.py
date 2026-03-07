from django import forms 
from .models import ProviderProfile, PortfolioImage 


class ProviderProfileForm(forms.ModelForm): 
    class Meta: 
        model = ProviderProfile
        fields = [ 'full_name', 'profile_picture', 'category', 'city', 'commune', 'bio', 'years_experience', 'hourly_rate', 'availability' ]
        widgets = { 
            'bio': forms.Textarea(attrs={'rows': 4}), 
        } 

class PortfolioImageForm(forms.ModelForm): 
    class Meta: 
        model = PortfolioImage
        fields = ['image', 'caption']