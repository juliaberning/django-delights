from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from .forms import IngredientForm, MenuItemForm, PurchaseForm, RecipeRequirementForm
from .models import Ingredient, MenuItem, Purchase, RecipeRequirement

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

class IngredientListView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = 'restaurant/ingredient_list.html'
    context_object_name = 'ingredients'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory_value'] = sum(
            [ingredient.price_per_unit * ingredient.quantity for ingredient in self.object_list]
        )
        return context

class IngredientCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = 'restaurant/ingredient_form.html'
    success_url = reverse_lazy('ingredient-list')

class IngredientUpdateView(LoginRequiredMixin, UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = 'restaurant/ingredient_form.html'
    success_url = reverse_lazy('ingredient-list')

class IngredientDeleteView(LoginRequiredMixin, DeleteView):
    model = Ingredient
    template_name = 'restaurant/delete.html'
    success_url = reverse_lazy('ingredient-list')
    context_object_name = 'obj'


# ----------------------------
# MenuItem Views
# ----------------------------
class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'restaurant/menu_item_list.html'
    context_object_name = 'menu_items'

class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurant/menu_item_form.html'
    success_url = reverse_lazy('menu-item-list')

    def form_valid(self, form):
        messages.success(self.request, 'Menu item created successfully!')
        return super().form_valid(form)

class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurant/menu_item_form.html'
    success_url = reverse_lazy('menu-item-list')

class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'restaurant/delete.html'
    success_url = reverse_lazy('menu-item-list')
    context_object_name = 'obj'

# ----------------------------
# RecipeRequirement Views
# ----------------------------

class RecipeRequirementCreateView(LoginRequiredMixin, CreateView):
    model = RecipeRequirement
    form_class = RecipeRequirementForm
    template_name = 'restaurant/recipe_requirement_form.html'

    def form_valid(self, form):
        try:
            self.object = form.save()
            messages.success(self.request, 'Recipe Requirement created successfully.')
            return redirect('recipe-requirement-detail', pk=self.object.menu_item.id)
        except IntegrityError:
            messages.warning(self.request, 'This ingredient is already linked to this menu item.')
            return redirect('recipe-requirement-create')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid form submission. Please check the data and try again.')
        return super().form_invalid(form)

class RecipeRequirementDetailView(LoginRequiredMixin, DetailView):
    model = MenuItem
    template_name = 'restaurant/recipe_requirement_detail.html'
    context_object_name = 'menu_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe_requirements'] = RecipeRequirement.objects.filter(menu_item=self.object)
        return context

class RecipeRequirementUpdateView(LoginRequiredMixin, UpdateView):
    model = RecipeRequirement
    form_class = RecipeRequirementForm
    template_name = 'restaurant/recipe_requirement_form.html'

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Recipe Requirement updated successfully.')
        return redirect('recipe-requirement-detail', pk=self.object.menu_item.id)

class RecipeRequirementDeleteView(LoginRequiredMixin, DeleteView):
    model = RecipeRequirement
    template_name = 'restaurant/delete.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('menu-item-list')

# ----------------------------
# Purchase Views
# ----------------------------



class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'restaurant/purchase_list.html'
    context_object_name = 'purchases'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate total revenue
        context['total_revenue'] = self.get_queryset().aggregate(
            total=Sum('menu_item__price')
        )['total'] or 0

        # Calculate total cost of inventory
        context['inventory_cost'] = Ingredient.objects.aggregate(
            total_cost=Sum(F('price_per_unit') * F('quantity'))
        )['total_cost'] or 0

        return context
    
class PurchaseCreateView(LoginRequiredMixin, FormView):
    template_name = 'restaurant/purchase_form.html'
    form_class = PurchaseForm

    def form_valid(self, form):
        purchase = form.save(commit=False)
        menu_item = purchase.menu_item

        # Validate inventory for all ingredients
        insufficient_stock = []
        for requirement in menu_item.reciperequirement_set.all():
            if requirement.ingredient.quantity < requirement.quantity:
                insufficient_stock.append(
                    f"{requirement.ingredient.name} (Required: {requirement.quantity}, Available: {requirement.ingredient.quantity})"
                )

        # If any ingredient is insufficient, show an error message
        if insufficient_stock:
            messages.error(
                self.request,
                "Cannot complete the purchase. Insufficient stock for the following ingredient(s): "
                + ", ".join(insufficient_stock)
            )
            return redirect('purchase-create')

        # Deduct inventory
        for requirement in menu_item.reciperequirement_set.all():
            requirement.ingredient.quantity -= requirement.quantity
            requirement.ingredient.save()

        # Save the purchase
        purchase.save()
        messages.success(self.request, f"Purchase of {menu_item.name} completed!")
        return redirect('purchase-list')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid form submission. Please check the data and try again.")
        return super().form_invalid(form)