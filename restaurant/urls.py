from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('create-ingredient/', views.create_ingredient, name='create_ingredient'),
    path('menu/', views.menu_item_list, name='menu_item_list'),
    path('create-menu-item/', views.create_menu_item, name='create_menu_item'),
]