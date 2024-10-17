from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_summary, name='panier_summary'),
    path('add/', views.cart_add, name='panier_add'),
    path('delete', views.cart_delete, name='panier_delete'),
    path('update', views.cart_update, name='panier_update'),
]
