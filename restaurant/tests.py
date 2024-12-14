from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Ingredient, MenuItem, Purchase, RecipeRequirement


class IngredientTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_create_ingredient(self):
        response = self.client.post(reverse('ingredient-create'), {
            'name': 'Tomato',
            'price_per_unit': 0.5,
            'quantity': 1000
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Ingredient.objects.filter(name='Tomato').exists())

    def test_list_ingredients(self):
        Ingredient.objects.create(name='Cheese', price_per_unit=1.5, quantity=500)
        response = self.client.get(reverse('ingredient-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cheese')


class MenuItemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_create_menu_item(self):
        response = self.client.post(reverse('menu-item-create'), {
            'name': 'Pizza',
            'price': 10.0
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(MenuItem.objects.filter(name='Pizza').exists())


class RecipeRequirementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.ingredient = Ingredient.objects.create(name='Tomato', price_per_unit=0.5, quantity=1000)
        self.menu_item = MenuItem.objects.create(name='Pizza', price=10.0)

    def test_create_recipe_requirement(self):
        response = self.client.post(reverse('recipe-requirement-create'), {
            'menu_item': self.menu_item.id,
            'ingredient': self.ingredient.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(RecipeRequirement.objects.filter(menu_item=self.menu_item, ingredient=self.ingredient).exists())


class PurchaseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.ingredient = Ingredient.objects.create(name='Tomato', price_per_unit=0.5, quantity=1000)
        self.menu_item = MenuItem.objects.create(name='Pizza', price=10.0)
        RecipeRequirement.objects.create(menu_item=self.menu_item, ingredient=self.ingredient, quantity=5)

    def test_purchase_sufficient_stock(self):
        response = self.client.post(reverse('purchase-create'), {
            'menu_item': self.menu_item.id,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after purchase
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.quantity, 995)  # Deducted 5 from stock

    def test_purchase_insufficient_stock(self):
        self.ingredient.quantity = 3  # Not enough stock
        self.ingredient.save()

        response = self.client.post(reverse('purchase-create'), {
            'menu_item': self.menu_item.id,
        }, follow=True)  # Follow the redirect

        self.assertEqual(response.status_code, 200)  # After redirect, it should load the page
        self.assertContains(response, 'Insufficient stock')  # Check for the error message

class InventoryAndRevenueTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.ingredient = Ingredient.objects.create(name='Cheese', price_per_unit=1.5, quantity=1000)
        self.menu_item = MenuItem.objects.create(name='Burger', price=8.0)

    def test_inventory_cost(self):
        response = self.client.get(reverse('ingredient-list'))
        inventory_cost = 1.5 * 1000  # price_per_unit * quantity
        self.assertEqual(response.context['inventory_value'], inventory_cost)

    def test_total_revenue(self):
        Purchase.objects.create(menu_item=self.menu_item)
        response = self.client.get(reverse('purchase-list'))
        total_revenue = 8.0  # One purchase of Burger
        self.assertEqual(response.context['total_revenue'], total_revenue)
