from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, {'template_name': 'ampacity'}),
    path('ampacity/', views.main, {'template_name': 'ampacity'}),
    path('voltdrop/', views.main, {'template_name': 'voltdrop'}),
    path('sctemprise/', views.main, {'template_name': 'sctemprise'}),
    path('report/', views.report),
]
