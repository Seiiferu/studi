from django.shortcuts import render, redirect
from panier.cart import Cart
from paiement.forms import ShippingForm, PaymentForm
from paiement.models import ShippingAddress, Order, OrderItem
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib import messages
from boutique.models import Product, Profile
import datetime

# Import des outils PayPal
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid # Identifiant utilisateur unique pour les commandes en double



def orders(request, pk):
	if request.user.is_authenticated and request.user.is_superuser:
		# Récupérer la commande
		order = Order.objects.get(id=pk)
		# Récupérer la commande
		items = OrderItem.objects.filter(order=pk)

		if request.POST:
			status = request.POST['shipping_status']
			# Vérifier  si c'est True ou False
			if status == "true":
				# Récupérer la commande
				order = Order.objects.filter(id=pk)
				# Mettre à jour le status
				now = datetime.datetime.now()
				order.update(shipped=True, date_shipped=now)
			else:
				# Récupérer la commande
				order = Order.objects.filter(id=pk)
				# Mettre à jour le status
				order.update(shipped=False)
			messages.success(request, "Statut d'expédition mis à jour")
			return redirect('category_summary')

		return render(request, 'paiement/orders.html', {"order":order, "items":items})

	else:
		messages.success(request, "Accès refusé")
		return redirect('category_summary')


def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False)
		order_items = OrderItem.objects.filter(order__in=orders)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Récupérer la commande
			order = Order.objects.filter(id=num)
			# Récupérer la date et l'heure
			now = datetime.datetime.now()
			# Mettre à jour la commande
			order.update(shipped=True, date_shipped=now)
			messages.success(request, "Statut d'expédition mis à jour")
			return redirect('category_summary')

		return render(request, "paiement/not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Accès refusé")
		return redirect('billetterie')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Récupérer la commande
			order = Order.objects.filter(id=num)
			# Récupérer la date et l'heure
			now = datetime.datetime.now()
			# Mettre à jour la commande
			order.update(shipped=False)
			messages.success(request, "Statut d'expédition mis à jour")
			return redirect('category_summary')

		return render(request, "paiement/shipped_dash.html", {"orders":orders})
	else:
		messages.error(request, "Accès refusé")
		return redirect('category_summary')

def order_summary(request):
	products = Product.objects.annotate(total_sales=Sum('orderitem__quantity'))
	return render(request, 'paiement/order_summary.html', {'products': products})


def process_order(request):
	if request.POST:
		# Récupérer le panier
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Obtenir les informations de facturation depuis la page précédente
		payment_form = PaymentForm(request.POST or None)

		# Obtenir les données d'expédition de la session
		my_shipping = request.session.get('my_shipping')
		# Rassembler les informations de la commande
		full_name = my_shipping['shipping_full_name']
		email = my_shipping['shipping_email']
		# Créer l'adresse d'expédition depuis les infos de la session
		shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
		amount_paid = totals

		if payment_form.is_valid():
			# Détails de la carte bancaire valide ? 
			card_number = request.POST.get('card_number')
			expiry_date = request.POST.get('card_exp_date')  # Utilisation correcte du champ
			cvv = request.POST.get('card_cvv_number')  # Utilisation correcte du champ

			if (
				card_number and len(card_number) == 16 and card_number.isdigit() and
				expiry_date and cvv and len(cvv) in [3, 4] and cvv.isdigit()
			):
				try:
					# MM/YY format
					expiry_month, expiry_year = expiry_date.split('/')
					expiry_month = int(expiry_month)
					expiry_year = int(expiry_year)

					# Convertir l'année en quatre chiffres si besoin
					if expiry_year < 100:
						expiry_year += 2000

					current_year = datetime.datetime.now().year
					current_month = datetime.datetime.now().month

					# Vérifier que la date d'expiration est bien antérieure et non postérieure
					if (expiry_year > current_year) or (expiry_year == current_year and expiry_month >= current_month):
						# Le format de la date d'expiration et du numéro de carte est correct
						payment_status = 'success'
					else:
						payment_status = 'failed'
						messages.error(request, "La date d'expiration n'est pas valide ou est déjà passée.")
				except ValueError:
					payment_status = 'failed'
					messages.error(request, "Erreur lors de l'analyse de la date d'expiration. Veuillez utiliser le format correct MM/AA.")
			else:
				payment_status = 'failed'
				messages.error(request, "Le numéro de carte, le CVV ou le format de la date d'expiration est incorrect.")
		else:
			payment_status = 'failed'
			messages.error(request, "Formulaire de paiement invalide. Veuillez corriger les erreurs et réessayer.")

		# Redirect based on payment_status
		if payment_status == 'success':
			messages.success(request, "Le paiement a réussi. Merci pour votre achat.")
			return redirect('payment_success')
		else:
			return redirect('payment_failed')


		# Créer une commande
		if request.user.is_authenticated:
			# Utilisateur connecté
			user = request.user
			# Créer une commande
			create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

            # Ajouter des articles à la commande
            # Obtenir l'ID de la commande
			order_id = create_order.pk
			
			# Récupérer les informations du produit
			for product in cart_products():
				# Récupérer l'ID du produit
				product_id = product.id
				# Récupérer le prix du produit
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Récupérer la quantité
				for key,value in quantities().items():
					if int(key) == product.id:
						# Créer une commande
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
						create_order_item.save()

			# Logique de traitement du paiement
			payment_status = process_payment(request)  # Retourne 'success' ou 'failed'

			# Vider le panier et rediriger en fonction du statut de paiement
			if payment_status == 'success':
				# Vider le panier
				cart.clear()
				# Vider la session/panier
				for key in list(request.session.keys()):
					if key == "session_key":
						del request.session[key]

				# Vider l'ancien panier du profil
				current_user = Profile.objects.filter(user__id=request.user.id)
				current_user.update(old_cart="")

				# Rediriger vers la page de succès
				messages.success(request, "Le paiement a réussi. Merci pour votre achat.")
				return redirect('payment_success')

			elif payment_status == 'failed':
				# Rediriger vers la page d'échec du paiement et retour à la caisse
				messages.error(request, "Le paiement a échoué. Veuillez réessayer.")
				return redirect('payment_failed')
				
		else:
            # Utilisateur non connecté
            # Créer la commande
			create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Ajouter une commande
			
			# Obtenir l'ID de la commande
			order_id = create_order.pk
			
			# Récupérer les informations du produit
			for product in cart_products():
				# Récupérer l'ID du produit
				product_id = product.id
				# Récupérer le prix du produit 
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Récupérer la quantité
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
						create_order_item.save()
			
			# Vider le panier
			cart.clear() 
			# Supprimer le panier
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]

			messages.success(request, "Commande passée !")
			return redirect('category_summary')

	else:
		messages.error(request, "Accès refusé")
		return redirect('category_summary')

def process_payment(request):
    # Ici, tu intègres le traitement réel du paiement via PayPal, Stripe, etc.
    # Simule le retour d'un statut de paiement pour l'exemple
    if 'valid_payment' in request.POST:  # Supposons que tu reçoives un paramètre qui valide le paiement
        return 'success'
    else:
        return 'failed'


def billing_info(request):
	if request.POST:
		# Récupérer le panier
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Créer une session à l'aide du formulaire d'expédition
		my_shipping = request.POST
		request.session['my_shipping'] = my_shipping

		# Get the host
		host = request.get_host()
		# Create Paypal Form Dictionary
		paypal_dict = {
			'business': settings.PAYPAL_RECEIVER_EMAIL,
			'amount': totals,
			'item_name': 'Book Order',
			'no_shipping': '2',
			'invoice': str(uuid.uuid4()),
			'currency_code': 'EUR', 
			'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
			'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
			'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
		}

		# Créatin d'un bouton PayPal
		paypal_form = PayPalPaymentsForm(initial=paypal_dict)

		# Vérifier si l'utilisateur est connecté 
		if request.user.is_authenticated:
			# Récupérer le formulaire de facturation
			billing_form = PaymentForm()
			return render(request, "paiement/billing_info.html", {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

		else:
			# Non connecté
			# Récupérer le formulaire de facturation
			billing_form = PaymentForm()
			return render(request, "paiement/billing_info.html", {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

		shipping_form = request.POST
		return render(request, "paiement/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})	
	else:
		messages.error(request, "Accès refusé")
		return redirect('category_summary')

def checkout(request):
	# Récupérer le panier
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()

	if request.user.is_authenticated:
		# Checkout  en tant qu'utilisatuer 
		# Formulaire d'expédition de l'utilisateur
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		# Formulaire de l'adresse d'expédition
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
		return render(request, "paiement/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form })
	else:
		# Checkout en tant qu'invité
		shipping_form = ShippingForm(request.POST or None)
		return render(request, "paiement/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})


def payment_success(request):
    messages.success(request, "Votre paiement a été accepté.")
    return render(request, 'paiement/payment_success.html')

def payment_failed(request):
    messages.error(request, "Votre paiement a échoué. Veuillez réessayer.")
    return render(request, 'paiement/payment_failed.html')



