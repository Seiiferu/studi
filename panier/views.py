from django.shortcuts import render, get_object_or_404
from .cart import Cart
from boutique.models import Product
from django.http import JsonResponse

from django.contrib import messages


def cart_summary(request):
    # Récupérer les données du panier
    panier = Cart(request)
    cart_products = panier.get_prods()
    quantities = panier.get_quants()
    totals = panier.cart_total()
    return render(request, "panier_summary.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals})

def cart_add(request):
    # Récupérer les données du panier
    cart = Cart(request)
    # teste pour POST
    if request.POST.get('action') == 'post':
        # Récupérer les produits
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # Rechercher le produit dans la db
        product = get_object_or_404(Product, id=product_id)

        # Sauvegarder la session
        cart.add(product=product, quantity=product_qty)

        # Récupérer la quantité des produits dans le panier
        cart_quantity = cart.__len__()

        # response = JsonResponse({'Product Name:': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, 'Item added to cart')

    return response

def cart_delete(request):
    # Ajouter la fonction supprimer dans le panier
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        # Appeler la fonction supprimer dans le panier
        cart.delete(product=product_id)

        response = JsonResponse({'product': product_id})
        # return redirect('cart_summary')
        messages.success(request, 'Item deleted')
        return response

def cart_update(request):
    # Ajouter la fonction mise à jour dans le panier
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # Appeler la fonction mise à jour dans le panier
        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty': product_qty})
        messages.success(request, 'Item updated')
        return response
