from django.shortcuts import render, redirect
from .models import Ingredient
from .forms import IngredientForm

def home(request):
    return render(request, 'restaurant/home.html')

def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'restaurant/ingredient_list.html', {'ingredients': ingredients})

def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ingredient_list')
    else:
        form = IngredientForm()
    return render(request, 'restaurant/ingredient_form.html', {'form': form})
