from django.test import TestCase
from django.urls import reverse
from paiement.models import Order, OrderItem
from boutique.models import Product, Category, Customer, Profile
from django.contrib.auth import get_user_model

class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            created_at="2024-10-18",
            shipped=False,
            amount_paid=1000
        )

    def test_order_creation(self):
        self.assertEqual(self.order.customer.first_name, "John")
        self.assertEqual(self.order.shipped, False)
        self.assertEqual(self.order.amount_paid, 1000)

class OrderItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="PARIS 2024", slug="paris-2024")
        self.product = Product.objects.create(
            name="Billet Solo",
            price=290,
            category=self.category,
            description="Billet pour les Jeux Olympiques PARIS 2024"
        )
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com"
        )
        self.order = Order.objects.create(customer=self.customer, date_ordered="2024-10-18", shipped=False)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=580
        )

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, 580)
