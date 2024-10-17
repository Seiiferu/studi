from .cart import Cart

def cart_summary(request):
    return {'panier': Cart(request)}