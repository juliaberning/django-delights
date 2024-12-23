import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from reportlab.pdfgen import canvas

from .forms import (IngredientForm, MenuItemForm, PurchaseForm,
                    RecipeRequirementForm)
from .models import Ingredient, MenuItem, Purchase, RecipeRequirement


def home(request):
    cards = [
        {
            "title": "Ingredients",
            "description": "Manage your ingredients effectively. View the inventory, add new ingredients, or update existing ones.",
            "url_name": "ingredient-list",
            "btn_text": "Go to Ingredients"
        },
        {
            "title": "Menu Items",
            "description": "Create and edit menu items for your restaurant. Link them to your ingredients for tracking.",
            "url_name": "menu-item-list",
            "btn_text": "Go to Menu Items"
        },
        {
            "title": "Recipes",
            "description": "Review all your recipes.",
            "url_name": "menu-with-ingredients",
            "btn_text": "Go to Recipes"
        },
        {
            "title": "Purchases",
            "description": "Track your purchases and inventory in one place. Stay on top of your stock.",
            "url_name": "purchase-list",
            "btn_text": "Go to Purchases"
        }
    ]
    return render(request, 'restaurant/home.html', {'cards': cards})

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
            messages.error(request, 'Invalid username or password. Please try again.', extra_tags='danger')
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
            messages.error(request, 'An error has occurred during registration', extra_tags='danger')
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

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['inventory_value'] = sum(
            [ingredient.price_per_unit * ingredient.quantity for ingredient in self.object_list]
        )
        return context

class IngredientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = 'restaurant/ingredient_form.html'
    success_url = reverse_lazy('ingredient-list')
    success_message = "%(name)s was created successfully!"    

class IngredientUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = 'restaurant/ingredient_form.html'
    success_url = reverse_lazy('ingredient-list')
    success_message = "%(name)s was updated successfully!"  

class IngredientDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Ingredient
    template_name = 'restaurant/delete.html'
    success_url = reverse_lazy('ingredient-list')
    context_object_name = 'obj'
    success_message = "Item was deleted successfully!" 

class IngredientPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Create a PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ingredient_list.pdf"'

        # Create the PDF object using ReportLab
        p = canvas.Canvas(response)

        # Query all ingredients
        ingredients = Ingredient.objects.all()

        # Set title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Ingredient List")

        # Add table headers
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 760, "Name")
        p.drawString(200, 760, "Quantity")
        p.drawString(350, 760, "Price Per Unit")
        p.drawString(450, 760, "Total Value")

        # Add data rows
        y = 740
        for ingredient in ingredients:
            total_value = ingredient.price_per_unit * ingredient.quantity

            p.setFont("Helvetica", 12)
            p.drawString(50, y, ingredient.name)
            p.drawString(200, y, str(ingredient.quantity))
            p.drawString(350, y, f"${ingredient.price_per_unit:.2f}")
            p.drawString(450, y, f"${total_value:.2f}")
            y -= 20  # Move to the next line

            if y < 50:  # Create a new page if space runs out
                p.showPage()
                y = 800

        # Finalize the PDF
        p.showPage()
        p.save()

        return response
    

class IngredientCSVView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        # Create a response object with the correct content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ingredients.csv"'

        # Create a CSV writer
        writer = csv.writer(response)

        # Write the header row
        writer.writerow(['Name', 'Quantity', 'Price per Unit'])

        # Write the ingredient data rows
        ingredients = Ingredient.objects.all()
        for ingredient in ingredients:
            writer.writerow([ingredient.name, ingredient.price_per_unit, ingredient.quantity])

        return response


# ----------------------------
# MenuItem Views
# ----------------------------
class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'restaurant/menu_item_list.html'
    context_object_name = 'menu_items'

class MenuItemCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurant/menu_item_form.html'
    success_url = reverse_lazy('menu-item-list')
    success_message = "%(name)s was created successfully!"  

class MenuItemUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurant/menu_item_form.html'
    success_url = reverse_lazy('menu-item-list')
    success_message = "%(name)s was updated successfully!" 

class MenuItemDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = MenuItem
    template_name = 'restaurant/delete.html'
    success_url = reverse_lazy('menu-item-list')
    context_object_name = 'obj'
    success_message = "Item was deleted successfully!" 

# ----------------------------
# RecipeRequirement Views
# ----------------------------

class RecipeRequirementCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = RecipeRequirement
    form_class = RecipeRequirementForm
    template_name = 'restaurant/recipe_requirement_form.html'
    success_message = "Recipe Requirement for %(menu_item)s and %(ingredient)s was created successfully!"

    def get_success_url(self):
        return reverse_lazy('recipe-requirement-detail', kwargs={'pk': self.object.menu_item.id})

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, 'This ingredient is already linked to this menu item.', extra_tags='danger')
            return self.render_to_response(self.get_context_data(form=form))


class RecipeRequirementDetailView(LoginRequiredMixin, DetailView):
    model = MenuItem
    template_name = 'restaurant/recipe_requirement_detail.html'
    context_object_name = 'menu_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe_requirements'] = RecipeRequirement.objects.filter(menu_item=self.object)
        return context

class RecipeRequirementUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = RecipeRequirement
    form_class = RecipeRequirementForm
    template_name = 'restaurant/recipe_requirement_form.html'
    success_message = "Recipe Requirement for %(menu_item)s and %(ingredient)s was updated successfully!"

    def get_success_url(self):
        return reverse_lazy('recipe-requirement-detail', kwargs={'pk': self.object.menu_item.id})


class RecipeRequirementDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = RecipeRequirement
    template_name = 'restaurant/delete.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('menu-item-list')
    success_message = "Item was deleted successfully!" 

@staff_member_required
def menu_with_ingredients_view(request):
    menu_items = MenuItem.objects.prefetch_related(
        'ingredients', 'reciperequirement_set'
    )  # Prefetch ingredients and recipe requirements
    return render(request, 'restaurant/menu_with_ingredients.html', {'menu_items': menu_items})

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
                + ", ".join(insufficient_stock), extra_tags='danger'
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
        messages.error(self.request, "Invalid form submission. Please check the data and try again.", extra_tags='danger')
        return super().form_invalid(form)
    
def total_purchases_dynamic(request):
    total_purchases = Purchase.objects.count()
    return JsonResponse({'total_purchases': total_purchases})

# ----------------------------
# Analytics View
# ----------------------------
@login_required(login_url='login')
def charts(request):
    return render(request, 'restaurant/charts.html')

@login_required(login_url='login')
def quantity_chart(request):
    labels = []
    data = []

    queryset = (
        RecipeRequirement.objects.values('ingredient__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')
    )

    for entry in queryset:
        labels.append(entry['ingredient__name'])
        data.append(entry['total_quantity'])


    response_data = {
        'labels': labels,
        'data': data,
        'chartTitle': 'Ingredient Usage Chart',
        'legend': 'Total Quantity', 
        'chartType': 'bar', 
    }

    return JsonResponse(data=response_data)

@login_required(login_url='login')
def revenue_chart(request):
    labels = []
    data = []

    menu_items = MenuItem.objects.all()
    names = [item.name for item in menu_items]
    revenues = [
        item.price * Purchase.objects.filter(menu_item=item).count()
        for item in menu_items
    ]   

    labels = names
    data = revenues

    response_data = {
        'labels': labels,
        'data': data,
        'chartTitle': 'Menu Item revenue Chart',
        'legend': 'Total Quantity', 
        'chartType': 'bar', 
    }

    return JsonResponse(data=response_data)

@login_required(login_url='login')
def inventory_chart(request):
    labels = []
    data = []

    ingredients = Ingredient.objects.all()
    
    labels = [ingredient.name for ingredient in ingredients]
    data = [ingredient.quantity for ingredient in ingredients]

    response_data = {
        'labels': labels,
        'data': data,
        'chartTitle': 'Inventory quantity Chart',
        'legend': 'Total Quantity', 
        'chartType': 'bar', 
    }

    return JsonResponse(data=response_data)
