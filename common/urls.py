from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('new/', views.new),
    path('disclaimer/', views.disclaimer),
    path('about/', views.about),
]



