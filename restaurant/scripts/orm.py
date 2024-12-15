from contextlib import contextmanager

from django.db import connection

from restaurant.models import Ingredient

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
