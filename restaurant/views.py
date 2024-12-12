from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .models import Ingredient, MenuItem
from .forms import IngredientForm, MenuItemForm

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
def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ingredient_list')
    else:
        form = IngredientForm()
    return render(request, 'restaurant/ingredient_form.html', {'form': form})


# ----------------------------
# MenuItem Views
# ----------------------------

@login_required(login_url='login')
def menu_item_list(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'restaurant/menu_item_list.html', {'menu_items': menu_items})

@login_required(login_url='login')
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item created successfully!')
            return redirect('menu_item_list')
    else:
        form = MenuItemForm()
    return render(request, 'restaurant/menu_item_form.html', {'form': form})