from django.contrib import admin
from .models import Category, Product, Customer, Profile, Order
from django.contrib.auth.models import User

# Admin Site(Admin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Profile)
admin.site.register(Order)

# Mélanger les informations de profil et les informations utilisateur
class ProfileInline(admin.StackedInline):
    model = Profile

# Étendre le modèle Utilisateur
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name','email']
    inlines = [ProfileInline]

# Désinscrire l'ancienne méthode
admin.site.unregister(User)

# Réinscrire la nouvelle méthode
admin.site.register(User, UserAdmin)