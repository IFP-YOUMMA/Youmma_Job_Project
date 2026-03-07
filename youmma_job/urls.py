from django.contrib import admin 
from django.urls import path, include 
from django.conf import settings 
from django.conf.urls.static import static 
from search import views


urlpatterns = [

    path('', views.home, name='home'),

    path('admin/', admin.site.urls), 
    path('users/', include('users.urls')),
    path('profiles/', include('profiles.urls')),
    path('reviews/', include('reviews.urls')),
    path('services/', include('services.urls')),
    path('search/', include('search.urls')),
    
    # Autres apps à ajouter plus tard
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)