from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('create-ingredient/', views.create_ingredient, name='create_ingredient'),
    path('update-ingredient/<str:pk>/', views.update_ingredient, name='update_ingredient'),
    path('delete-ingredient/<str:pk>/', views.delete_ingredient, name='delete_ingredient'),
    path('menu/', views.menu_item_list, name='menu_item_list'),
    path('create-menu-item/', views.create_menu_item, name='create_menu_item'),
    path('update-menu-item/<str:pk>/', views.update_menu_item, name='update_menu_item'),
    path('delete-menu-item/<str:pk>/', views.delete_menu_item, name='delete_menu_item'),
]