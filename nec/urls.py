from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, {'template_name': 'ampacity'}),
    path('ampacity/', views.main, {'template_name': 'ampacity'}),
    path('voltdrop/', views.main, {'template_name': 'voltdrop'}),
    path('report/', views.report),
]
