from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/add/', views.add_ingredient, name='add_ingredient'),
]