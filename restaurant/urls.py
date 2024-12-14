from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Authentication URLs
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),

    # Ingredient URLs
    path('ingredients/', views.ingredient_list, name='ingredient-list'),
    path('ingredient/create/', views.create_ingredient, name='ingredient-create'),
    path('ingredient/<str:pk>/update/', views.update_ingredient, name='ingredient-update'),
    path('ingredient/<str:pk>/delete/', views.delete_ingredient, name='ingredient-delete'),

    # MenuItem URLs
    path('menu-items/', views.menu_item_list, name='menu-item-list'),
    path('menu-item/create/', views.create_menu_item, name='menu-item-create'),
    path('menu-item/<str:pk>/update/', views.update_menu_item, name='menu-item-update'),
    path('menu-item/<str:pk>/delete/', views.delete_menu_item, name='menu-item-delete'),

    # RecipeRequirement URLs
    
    path('recipe-requirement/<str:pk>/', views.recipe_requirement_detail, name='recipe-requirement-detail'),
    path('recipe-requirement/create/', views.create_recipe_requirement, name='recipe-requirement-create'),
    path('requirement/<str:pk>/update/', views.update_recipe_requirement, name='recipe-requirement-update'),
    path('recipe-requirement/<str:pk>/delete', views.delete_recipe_requirement, name='recipe-requirement-delete'),

    # Purchase URLs
    path('purchases/', views.purchase_list, name='purchase-list'),
    path('purchase/create/', views.create_purchase, name='purchase-create'),
    
]