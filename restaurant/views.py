from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .models import Ingredient, MenuItem, RecipeRequirement
from .forms import IngredientForm, MenuItemForm, RecipeRequirementForm

def home(request):
    return render(request, 'restaurant/home.html')

# ----------------------------
# Authentication Views
# ----------------------------


def loginPage(request):
    if request.user.is_authenticated:
            return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'restaurant/login_register.html', {'page': 'login'})


def logoutUser(request):
    logout(request)
    return redirect('home')
def registerPage(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
        else: 
            messages.error(request, 'An error has occurred during registration')
    else:
        form = UserCreationForm()
    return render(request, 'restaurant/login_register.html', {'form': form})

# ----------------------------
# Ingredient Views
# ----------------------------

@login_required(login_url='login')
def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    inventory_value = sum([ingredient.price_per_unit * ingredient.quantity for ingredient in ingredients])
    context = {'ingredients': ingredients, 'inventory_value': inventory_value}
    return render(request, 'restaurant/ingredient_list.html', context)

@login_required(login_url='login')
def create_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ingredient_list')
    else:
        form = IngredientForm()
    return render(request, 'restaurant/ingredient_form.html', {'form': form})

@login_required(login_url='login')
def update_ingredient(request, pk):
    ingredient = Ingredient.objects.get(id=pk)
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            return redirect('ingredient_list')
    else:
        form = IngredientForm(instance=ingredient)
    return render(request, 'restaurant/ingredient_form.html', {'form': form})

@login_required(login_url='login')
def delete_ingredient(request, pk):
    ingredient = Ingredient.objects.get(id=pk)
    if request.method == 'POST':
        ingredient.delete()
        return redirect('ingredient_list')
    return render(request, 'restaurant/delete.html', {'obj': ingredient})


# ----------------------------
# MenuItem Views
# ----------------------------

@login_required(login_url='login')
def menu_item_list(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'restaurant/menu_item_list.html', {'menu_items': menu_items})

@login_required(login_url='login')
def create_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item created successfully!')
            return redirect('menu_item_list')
    else:
        form = MenuItemForm()
    return render(request, 'restaurant/menu_item_form.html', {'form': form})

@login_required(login_url='login')
def update_menu_item(request, pk):
    menu_item = MenuItem.objects.get(id=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menu_item)
        if form.is_valid():
            form.save()
            return redirect('menu_item_list')
    else:
        form = MenuItemForm(instance=menu_item)
    return render(request, 'restaurant/menu_item_form.html', {'form': form})

@login_required(login_url='login')
def delete_menu_item(request, pk):
    menu_item = MenuItem.objects.get(id=pk)
    if request.method == 'POST':
        menu_item.delete()
        return redirect('menu_item_list')
    return render(request, 'restaurant/delete.html', {'obj': menu_item})

# ----------------------------
# RecipeRequirement Views
# ----------------------------

@login_required(login_url='login')
def create_recipe_requirement(request):
    if request.method == 'POST':
        form = RecipeRequirementForm(request.POST)
        if form.is_valid():
            try:
                recipe_requirement = form.save()
                messages.success(request, 'Recipe Requirement created successfully.')
                return redirect('recipe_requirement_detail', pk=recipe_requirement.menu_item.id)
            except IntegrityError:
                messages.warning(request, 'This ingredient is already linked to this menu item.')
                return redirect('create-recipe-requirement') 
        else:
            messages.error(request, 'Invalid form submission. Please check the data and try again.')
    else:
        form = RecipeRequirementForm()

    return render(request, 'restaurant/recipe_requirement_form.html', {'form': form})

def recipe_requirement_detail(request, pk):
    menu_item = MenuItem.objects.get(id=pk)
    recipe_requirements = RecipeRequirement.objects.filter(menu_item=menu_item)
    return render(request, 'restaurant/recipe_requirement_detail.html', {'menu_item': menu_item, 'recipe_requirements': recipe_requirements})

def update_recipe_requirement(request, pk):
    recipe_requirement = RecipeRequirement.objects.get(id=pk)
    if request.method == 'POST':
        form = RecipeRequirementForm(request.POST, instance=recipe_requirement)
        if form.is_valid():
            form.save()
            return redirect('recipe_requirement_detail', pk=recipe_requirement.menu_item.id)
    else:
        form = RecipeRequirementForm(instance=recipe_requirement)
    return render(request, 'restaurant/recipe_requirement_form.html', {'form': form})

@login_required(login_url='login')
def delete_recipe_requirement(request, pk):
    recipe_requirement = RecipeRequirement.objects.get(id=pk)
    if request.method == 'POST':
        recipe_requirement.delete()
        return redirect('menu_item_list')
    return render(request, 'restaurant/delete.html', {'obj': recipe_requirement})
