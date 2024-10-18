from django.test import TestCase
from django.urls import reverse
from boutique.models import Product, Category, Customer, Profile, Order
from paiement.models import Order, OrderItem
from django.contrib.auth import get_user_model

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="PARIS 2024", slug="paris-2024")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "PARIS 2024")
        self.assertEqual(self.category.slug, "paris-2024")

class CategoryViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="PARIS 2024", slug="paris-2024")
        self.product = Product.objects.create(
            name="Billet Solo",
            price=290,
            category=self.category,
            description="Billet pour les Jeux Olympiques PARIS 2024",
            is_sale=True,
            sale_price=260,
        )

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="PARIS 2024", slug="paris-2024")
        self.product = Product.objects.create(
            name="Billet Solo",
            price=290,
            category=self.category,
            description="Billet pour les Jeux Olympiques PARIS 2024",
            is_sale=True,
            sale_price=260,
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Billet Solo")
        self.assertEqual(self.product.price, 290)
        self.assertEqual(self.product.category.name, "PARIS 2024")
        self.assertTrue(self.product.is_sale)
        self.assertEqual(self.product.sale_price, 260)

class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            address="123 Main St",
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.first_name, "John")
        self.assertEqual(self.customer.last_name, "Doe")
        self.assertEqual(self.customer.email, "johndoe@example.com")
        self.assertEqual(self.customer.address, "123 Main St")


class ProfileModelTest(TestCase):
    def setUpTestData(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.profile = Profile.objects.create(
            user=self.user,
            address1="123 Main St",
            address2="Apt 4B",
            city="Paris",
            state="Île-de-France",
            zipcode="75001",
            country="France",
            phone="1234567890"
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.city, "Paris")


class AuthenticationTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

    def test_login_view(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())