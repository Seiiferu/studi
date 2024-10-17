from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Category, Product, Profile

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm

from paiement.forms import ShippingForm
from paiement.models import ShippingAddress

from django import forms
from django.db.models import Q
import json
from panier.cart import Cart

def accueil(request):
	return render(request, 'accueil.html', {})

def nous(request):
    return render(request, 'nous.html', {})


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories})

def category(request, foo):
    foo = foo.replace('-', ' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:
        messages.error(request, 'Oups! Catégorie invalide, veuillez réessayer...')
        return redirect('category_summary')

def product_detail(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product_detail.html', {'product': product})

def search(request):
    # Determine if they filled out the formm
    if request.method == 'POST':
        searched = request.POST['searched']
        # Query The Products DB Model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test for null
        if not searched:
            messages.error(request, 'Aucun résultat trouvé')
            return render(request,'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched})
    else:
        return render(request, 'search.html', {})


def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)

			# Gestion du panier d'achat
			current_user = Profile.objects.get(user=request.user)

			# Obtenir le panier enregistré depuis la base de données
			saved_cart = current_user.old_cart
			# Convertir la db vers la bibliothèque Py
			if saved_cart:
				# Convertir vers la biliothèque en utilisant JSON
				converted_cart = json.loads(saved_cart)
				# Ajouter le panier enregistrer dans le panier dans la session
				# Récupérer le panier
				cart = Cart(request)
				# Parcourir le panier et ajouter les articles depuis la db
				for key,value in converted_cart.items():
					cart.db_add(product=key, quantity=value)

			messages.success(request, ("Vous êtes connecté !"))
			return redirect('category_summary')
		else:
			messages.error(request, ("Erreur, veuillez réessayer..."))
			return redirect('login')

	else:
		return render(request, 'login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ("Vous êtes déconnecté... Merci de votre visite..."))
	return redirect('category_summary')

def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# Connextion en tant qu'utilisatuer
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Nom d'utilisateur créé - Veuillez remplir vos informations ci-dessous..."))
			return redirect('update_info')
		else:
			messages.error(request, ("Oups! Problème lors de l'inscription, veuillez réessayer..."))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form':form})

def update_info(request):
	if request.user.is_authenticated:
		# Récupérer l'utilisateur
		current_user = Profile.objects.get(user__id=request.user.id)
		# Récupérer les informations d'expédition de l'utilisateur 
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		
		# Récupérer le formulaire d'origine de l'utilisateur 
		form = UserInfoForm(request.POST or None, instance=current_user)
		# Récupérer le formulaire d'expédition de l'utilisateur
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)		
		if form.is_valid() or shipping_form.is_valid():
			# Sauvegarder le formulaire d'origine
			form.save()
			# Sauvegarder le formulaire d'expédition
			shipping_form.save()

			messages.success(request, "Vos informations ont été mises à jour !!")
			return redirect('category_summary')
		return render(request, "update_info.html", {'form':form, 'shipping_form':shipping_form})
	else:
		messages.warning(request, "Vous devez être connecté pour accéder à cette page !!")
		return redirect('update_user')


def update_password(request):
	if request.user.is_authenticated:
		current_user = request.user
		# Le formulaire a t-il été remplis ? 
		if request.method  == 'POST':
			form = ChangePasswordForm(current_user, request.POST)
			# Is the form valid
			if form.is_valid():
				form.save()
				messages.success(request, "Votre mot de passe a été mis à jour...")
				login(request, current_user)
				return redirect('update_user')
			else:
				for error in list(form.errors.values()):
					messages.error(request, error)
					return redirect('update_password')
		else:
			form = ChangePasswordForm(current_user)
			return render(request, "update_password.html", {'form':form})
	else:
		messages.warning(request, "Vous devez être connecté pour voir cette page...")
		return redirect('category_summary')

def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		user_form = UpdateUserForm(request.POST or None, instance=current_user)

		if user_form.is_valid():
			user_form.save()

			login(request, current_user)
			messages.success(request, "Utilisateur mis à jour !!")
			return redirect('category_summary')
		return render(request, "update_user.html", {'user_form':user_form})
	else:
		messages.warning(request, "Vous devez être connecté pour accéder à cette page !!")
		return redirect('category_summary')
