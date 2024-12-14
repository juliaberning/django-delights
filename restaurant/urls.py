from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Authentication URLs
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),

    # Ingredient URLs
    path('ingredients/', views.IngredientListView.as_view(), name='ingredient-list'),
    path('ingredient/create/', views.IngredientCreateView.as_view(), name='ingredient-create'),
    path('ingredient/<int:pk>/update/', views.IngredientUpdateView.as_view(), name='ingredient-update'),
    path('ingredient/<int:pk>/delete/', views.IngredientDeleteView.as_view(), name='ingredient-delete'),

    # MenuItem URLs
    path('menu-items/', views.MenuItemListView.as_view(), name='menu-item-list'),
    path('menu-item/new/', views.MenuItemCreateView.as_view(), name='menu-item-create'),
    path('menu-item/<int:pk>/edit/', views.MenuItemUpdateView.as_view(), name='menu-item-update'),
    path('menu-item/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='menu-item-delete'),

    # RecipeRequirement URLs
    path('recipe-requirement/new/', views.RecipeRequirementCreateView.as_view(), name='recipe-requirement-create'),
    path('recipe-requirement/<int:pk>/', views.RecipeRequirementDetailView.as_view(), name='recipe-requirement-detail'),
    path('recipe-requirement/<int:pk>/edit/', views.RecipeRequirementUpdateView.as_view(), name='recipe-requirement-update'),
    path('recipe-requirement/<int:pk>/delete/', views.RecipeRequirementDeleteView.as_view(), name='recipe-requirement-delete'),

    # Purchase URLs
    path('purchases/', views.PurchaseListView.as_view(), name='purchase-list'),
    path('purchase/new/', views.PurchaseCreateView.as_view(), name='purchase-create'),
]