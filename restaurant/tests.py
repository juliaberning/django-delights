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
        self.user = User.objects.create_user(username='testuser', password='password', is_staff=True)
        self.client.login(username='testuser', password='password')
        self.ingredient = Ingredient.objects.create(name='Cheese', price_per_unit=1.5, quantity=1000)
        self.menu_item = MenuItem.objects.create(name='Burger', price=8.0)

    def test_inventory_cost(self):
        response = self.client.get(reverse('ingredient-list'))
        inventory_cost = 1.5 * 1000  # price_per_unit * quantity
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['inventory_value'], inventory_cost)

    def test_total_revenue(self):
        Purchase.objects.create(menu_item=self.menu_item)
        response = self.client.get(reverse('purchase-list'))
        total_revenue = 8.0  # One purchase of Burger
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_revenue'], total_revenue)

class IngredientPDFViewTest(TestCase):
    def setUp(self):
        # Set up test client and log in user
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Create test ingredients
        self.ingredient1 = Ingredient.objects.create(name="Flour", quantity=10, price_per_unit=1.5)
        self.ingredient2 = Ingredient.objects.create(name="Sugar", quantity=5, price_per_unit=2.0)

    def test_pdf_view_response(self):
        # Access the PDF view
        response = self.client.get(reverse('ingredient-pdf'))

        # Test that the response is successful
        self.assertEqual(response.status_code, 200)

        # Test that the response is of type PDF
        self.assertEqual(response['Content-Type'], 'application/pdf')

        # Test that the filename is correct
        self.assertIn('ingredient_list.pdf', response['Content-Disposition'])

    def test_pdf_content(self):
        # Access the PDF view
        response = self.client.get(reverse('ingredient-pdf'))

        # Verify that the response contains valid PDF content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

        # Check that the content starts with the PDF file header
        self.assertTrue(response.content.startswith(b"%PDF"), "The PDF content does not start with %PDF")

class IngredientCSVViewTest(TestCase):
    def setUp(self):
        # Set up test user and ingredients
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        Ingredient.objects.create(name="Flour", price_per_unit=1.5, quantity=10)
        Ingredient.objects.create(name="Sugar", price_per_unit=2.0, quantity=5)

    def test_csv_view(self):
        response = self.client.get(reverse('ingredient-csv'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the response is a CSV file
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="ingredients.csv"', response['Content-Disposition'])

        # Check that the CSV content includes the ingredient data
        csv_content = response.content.decode('utf-8')
        self.assertIn("Flour", csv_content)
        self.assertIn("Sugar", csv_content)

class TotalPurchasesDynamicTest(TestCase):

    def setUp(self):
        # Create a sample menu item and purchases
        self.burger = MenuItem.objects.create(name="Burger", price=5.0)
        Purchase.objects.create(menu_item=self.burger)
        Purchase.objects.create(menu_item=self.burger)

    def test_total_purchases_dynamic(self):
        # Simulate an dynamic GET request to the endpoint
        url = reverse('total-purchases-dynamic')
        response = self.client.get(url)

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        json_response = response.json()

        # Assert the JSON structure and content
        self.assertIn('total_purchases', json_response)
        self.assertEqual(json_response['total_purchases'], 2)  # Expecting 2 purchases