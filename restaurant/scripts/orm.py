from contextlib import contextmanager

from django.db import connection

from restaurant.models import Ingredient, MenuItem, RecipeRequirement, Purchase

"""
Django ORM Script

Purpose:
This script demonstrates the use of Django's ORM to interact with a database.
Optionally, it outputs the raw SQL queries executed during these operations for debugging and performance analysis.

Usage:
    -Set LOGGING_ENABLED to True to log queries.
    -Run this script using Django Extensions' `runscript` command:
        python manage.py runscript orm_script
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

    """Query primary key of ingredient"""

    with log_queries("Create ingredient with .save()"):
        ingredient = Ingredient(name='Tomato', price_per_unit=0.5, quantity=1000)
        ingredient.save()
        print(f"Created ingredient with .save() - Output: {ingredient.name}")

    with log_queries("Delete ingredient with .delete()"):
        ingredient.delete()
        print(f"Deleted ingredient with .delete() - Output: {ingredient.name}")

    with log_queries("Create ingredient with .create()"):
        ingredient = Ingredient.objects.create(name='Onion', price_per_unit=0.3, quantity=500)
        print(f"Created ingredient with .create() - Output: {ingredient.name}")

    with log_queries("Remove duplicate ingredients"):
        ingredients = Ingredient.objects.filter(name='Onion').order_by('-quantity')[1:]
        for duplicate in ingredients:
            duplicate.delete()
            print(f"Deleted duplicate ingredient - Output: {duplicate.name}")

    with log_queries("Fetch single Tomato ingredient"):
        ingredient = Ingredient.objects.get(name='Tomato')
        print(f"Amount of units - Output: {ingredient.name}: {ingredient.quantity}")

    with log_queries("Count Tomato instances"):
        tomatoes = Ingredient.objects.filter(name='Tomato')
        print(f"Number of tomato instances - Output: {tomatoes.count()}")

    with log_queries("Update quantity of Tomato"):
        ingredient.quantity = 800
        ingredient.save()
        print(f"Updated quantity -Output: Updated {ingredient.name} to {ingredient.quantity} units")

    with log_queries("Fetch first ingredient"):
        ingredient = Ingredient.objects.first()
        print(f"First ingredient - Output: {ingredient.name}")

    with log_queries("Fetch third ingredient by position"):
        ingredient = Ingredient.objects.all()[2]
        print(f"Third ingredient - Output: {ingredient.name}")

    with log_queries("Fetch last three ingredients"):
        ingredients = Ingredient.objects.all().order_by('-id')[:3]
        print("Last three ingredients - Output:")
        for ingredient in ingredients:
            print(ingredient.name)

    with log_queries("Fetch all ingredients"):
        ingredients = Ingredient.objects.all()
        print("Ingredients - Output:")
        for ingredient in ingredients:
            print(f"{ingredient.name}: {ingredient.quantity} units")

    with log_queries("Fetch ingredients with quantity < 5"):
        ingredients = Ingredient.objects.filter(quantity__lt=5)
        ingredients_count = ingredients.count()
        print("Ingredients with quantity less than 5 - Output:")
        for ingredient in ingredients:
            print(f"{ingredient.name}: {ingredient.quantity} units")
        print(f"Number of ingredients with quantity < 5 - Output: {ingredients_count}")

    with log_queries("Count ingredients"):
        ingredients_count = Ingredient.objects.count()
        print(f"Number of ingredients - Output: {ingredients_count}")

    """
    Make queries with related models
    """

    with log_queries("Create or get ingredients - Tomato"):
        tomato, created = Ingredient.objects.get_or_create(
            name="Tomato",
            defaults={"price_per_unit": 0.5, "quantity": 100}
        )
        if created:
            print(f"Created new ingredient: {tomato.name}")
        else:
            print(f"Ingredient already exists: {tomato.name}")

    with log_queries("Create or get ingredients - Cheese"):
        cheese, created = Ingredient.objects.get_or_create(
            name="Cheese",
            defaults={"price_per_unit": 2.0, "quantity": 50}
        )
        if created:
            print(f"Created new ingredient: {cheese.name}")
        else:
            print(f"Ingredient already exists: {cheese.name}")

    with log_queries("Create or get ingredients - Lettuce"):
        lettuce, created = Ingredient.objects.get_or_create(
            name="Lettuce",
            defaults={"price_per_unit": 0.3, "quantity": 75}
        )
        if created:
            print(f"Created new ingredient: {lettuce.name}")
        else:
            print(f"Ingredient already exists: {lettuce.name}")

    with log_queries("Create or get menu item - Burger"):
        burger, created = MenuItem.objects.get_or_create(
            name="Burger",
            defaults={"price": 5.0}
        )
        if created:
            print(f"Created new menu item: {burger.name}")
        else:
            print(f"Menu item already exists: {burger.name}")

    with log_queries("Link ingredient to menu item - Tomato"):
        recipe, created = RecipeRequirement.objects.get_or_create(
            menu_item=burger,
            ingredient=tomato,
            defaults={"quantity": 2.0}
        )
        if created:
            print(f"Created recipe requirement: {recipe.ingredient.name} for {recipe.menu_item.name}")
        else:
            print(f"Recipe requirement already exists: {recipe.ingredient.name} for {recipe.menu_item.name}")

    with log_queries("Link ingredient to menu item - Cheese"):
        recipe, created = RecipeRequirement.objects.get_or_create(
            menu_item=burger,
            ingredient=cheese,
            defaults={"quantity": 1.0}
        )
        if created:
            print(f"Created recipe requirement: {recipe.ingredient.name} for {recipe.menu_item.name}")
        else:
            print(f"Recipe requirement already exists: {recipe.ingredient.name} for {recipe.menu_item.name}")

    with log_queries("Link ingredient to menu item - Lettuce"):
        recipe, created = RecipeRequirement.objects.get_or_create(
            menu_item=burger,
            ingredient=lettuce,
            defaults={"quantity": 0.5}
        )
        if created:
            print(f"Created recipe requirement: {recipe.ingredient.name} for {recipe.menu_item.name}")
        else:
            print(f"Recipe requirement already exists: {recipe.ingredient.name} for {recipe.menu_item.name}")

    with log_queries("Fetch all ingredients required for Burger"):
        burger_ingredients = burger.ingredients.all()
        for ingredient in burger_ingredients:
            print(f"{ingredient.name} is required for {burger.name}")

    with log_queries("Fetch all RecipeRequirement entries for Burger"):
        burger_requirements = RecipeRequirement.objects.filter(menu_item=burger)
        print("Recipe requirements for the Burger menu item:")
        for req in burger_requirements:
            print(f"{req.quantity} of {req.ingredient.name} is required for {req.menu_item.name}")

    with log_queries("Find all menu items that require Tomato"):
        menu_items_with_tomato = MenuItem.objects.filter(ingredients__name="Tomato")
        for item in menu_items_with_tomato:
            print(f"{item.name} uses Tomato")

    with log_queries("Record a purchase of Burger"):
        purchase = Purchase.objects.create(menu_item=burger)
        print("Purchase recorded:", purchase)

    with log_queries("Reduce stock of ingredients for Burger"):
        burger_requirements = RecipeRequirement.objects.filter(menu_item=burger)
        for req in burger_requirements:
            req.ingredient.quantity -= req.quantity  # Deduct the required amount
            req.ingredient.save()

    with log_queries("Print updated ingredient quantities"):
        for ingredient in burger.ingredients.all():
            print(f"{ingredient.name}: {ingredient.quantity} units remaining")


    # with log_queries("Delete Burger and its recipe requirements"):
    #     burger.delete()
