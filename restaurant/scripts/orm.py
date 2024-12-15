from contextlib import contextmanager

from django.db import connection, transaction
from django.db.models import F, Sum

from restaurant.models import Ingredient, MenuItem, Purchase, RecipeRequirement

"""
Django ORM Script

Purpose:
This script demonstrates the use of Django's ORM to interact with a database.
Each section highlights a specific query operation or relationship.
"""

@contextmanager
def log_queries(label):
    """Logs the queries executed within the context."""
    if not LOGGING_ENABLED:
        yield
        return
    initial_queries = len(connection.queries)
    yield
    new_queries = connection.queries[initial_queries:]
    for query in new_queries:
        print(f"{label}: {query['sql']}")
        print(f"Time: {query['time']}")
    print("----------------------------------------------------")


def run():
    global LOGGING_ENABLED
    LOGGING_ENABLED = True

    # SECTION 1: Queries with the Primary Key
    print("\n### Queries with the Primary Key ###")
    with log_queries("Create Ingredient"):
        ingredient = Ingredient.objects.create(name="Tomato", price_per_unit=0.5, quantity=100)
        print(f"Created Ingredient: {ingredient.name}, ID: {ingredient.id}")

    with log_queries("Fetch Ingredient by ID"):
        ingredient = Ingredient.objects.get(pk=ingredient.id)
        print(f"Fetched Ingredient: {ingredient.name}, Quantity: {ingredient.quantity}")

    with log_queries("Update Ingredient"):
        ingredient.quantity = 150
        ingredient.save()
        print(f"Updated Quantity: {ingredient.quantity}")

    with log_queries("Delete Ingredient"):
        ingredient.delete()
        print("Ingredient Deleted")

    # SECTION 2: Queries with a Foreign Key Relationship
    print("\n### Queries with a Foreign Key Relationship ###")
    with log_queries("Create MenuItem and Link Ingredients"):
        burger = MenuItem.objects.create(name="Burger", price=5.0)
        tomato = Ingredient.objects.create(name="Tomato", price_per_unit=0.5, quantity=100)
        lettuce = Ingredient.objects.create(name="Lettuce", price_per_unit=0.3, quantity=50)
        cheese = Ingredient.objects.create(name="Cheese", price_per_unit=2.0, quantity=20)
        
        RecipeRequirement.objects.create(menu_item=burger, ingredient=tomato, quantity=2)
        RecipeRequirement.objects.create(menu_item=burger, ingredient=lettuce, quantity=1)
        RecipeRequirement.objects.create(menu_item=burger, ingredient=cheese, quantity=0.5)
        print(f"Linked Ingredients to MenuItem: {burger.name}")

    # SECTION 3: Reversed Queries of a Foreign Key Relationship
    print("\n### Reversed Queries of a Foreign Key Relationship ###")
    with log_queries("Fetch MenuItems that use Tomato"):
        tomato_related_items = tomato.menuitem_set.all()
        for item in tomato_related_items:
            print(f"MenuItem Using Tomato: {item.name}")

    with log_queries("Fetch Purchases of Burger"):
        purchase = Purchase.objects.create(menu_item=burger)
        for purchase in burger.purchase_set.all():
            print(f"Burger Purchased at: {purchase.timestamp}")

    # SECTION 4: Queries with a Join Table
    print("\n### Queries with a Join Table ###")
    with log_queries("Fetch RecipeRequirements for Burger"):
        burger_requirements = RecipeRequirement.objects.filter(menu_item=burger)
        for req in burger_requirements:
            print(f"{req.quantity} {req.ingredient.name} required for {burger.name}")

    # SECTION 5: Filters
    print("\n### Filters ###")
    with log_queries("Filter Ingredients with Quantity < 50"):
        low_stock_ingredients = Ingredient.objects.filter(quantity__lt=50)
        for ingredient in low_stock_ingredients:
            print(f"Low Stock: {ingredient.name} ({ingredient.quantity} units)")

    with log_queries("Exclude Ingredients with Name 'Tomato'"):
        other_ingredients = Ingredient.objects.exclude(name="Tomato")
        for ingredient in other_ingredients:
            print(f"Ingredient: {ingredient.name}")


    # SECTION 6: Aggregates
    print("\n### Aggregates ###")
    with log_queries("Count All Ingredients"):
        ingredient_count = Ingredient.objects.count()
        print(f"Total Ingredients: {ingredient_count}")

    with log_queries("Sum of All Ingredient Quantities"):
        total_quantity = Ingredient.objects.aggregate(total=Sum('quantity'))['total']
        print(f"Total Quantity of Ingredients: {total_quantity}")

    print("\n### Ordering Results ###")
    with log_queries("Order Ingredients by Name (Ascending)"):
        ordered_ingredients = Ingredient.objects.order_by("name")
        for ingredient in ordered_ingredients:
            print(f"Ingredient: {ingredient.name} (Quantity: {ingredient.quantity})")

    with log_queries("Order Ingredients by Quantity (Descending)"):
        ordered_ingredients = Ingredient.objects.order_by("-quantity")
        for ingredient in ordered_ingredients:
            print(f"Ingredient: {ingredient.name} (Quantity: {ingredient.quantity})")

    # SECTION 7: Calculations
    print("\n### Calculations ###")
    with log_queries("Reduce Stock for Burger Purchase"):
        requirements = RecipeRequirement.objects.filter(menu_item=burger)
        for req in requirements:
            req.ingredient.quantity -= req.quantity
            req.ingredient.save()
            print(f"Updated Stock: {req.ingredient.name} ({req.ingredient.quantity} units remaining)")

    with log_queries("Fetch Ingredients with Derived Field"):
        ingredients = Ingredient.objects.annotate(total_cost=F("quantity") * F("price_per_unit"))
        for ingredient in ingredients:
            print(f"{ingredient.name}: Total Cost = {ingredient.total_cost}")

    with log_queries("Complex Query with Joins, Filters, Annotations, Aggregation, and Ordering"):
        # Complex Query
        results = (
            RecipeRequirement.objects
            .select_related("menu_item", "ingredient")  # Optimizes JOINs
            .filter(
                menu_item__name="Burger",         # Filter by related model field
                ingredient__quantity__gte=10,    # Filter by ingredient stock
            )
            .annotate(
                total_cost=F("ingredient__price_per_unit") * F("quantity"),  # Annotation for cost
            )
            .values(
                "menu_item__name",               # Only return specific fields
                "ingredient__name",
                "quantity",
                "total_cost",
            )
            .order_by("-total_cost")             # Order by calculated field
            .aggregate(
                total_ingredient_cost=Sum("total_cost")  # Aggregation for total cost
            )
        )

        # Output Results
        print("Complex Query Result:")
        print(f"Total Ingredient Cost: {results['total_ingredient_cost']}")
