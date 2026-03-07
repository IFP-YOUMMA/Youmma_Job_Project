from django.contrib import admin 
from .models import ServiceCategory 

@admin.register(ServiceCategory) 
class ServiceCategoryAdmin(admin.ModelAdmin): 
    list_display = ['name', 'slug', 'is_active', 'order'] 
    list_editable = ['is_active', 'order'] 
    prepopulated_fields = {'slug': ('name',)}