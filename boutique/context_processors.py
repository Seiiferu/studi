from .models import Category

def navbar_context(request):
    categories = Category.objects.all()
    return {"categories": categories}