from django.urls import path
from . import views

urlpatterns = [
    path('', views.help),
    path('getting_started/', views.get_started),
    path('principles/', views.principles),
    path('nec_tutorial/', views.nec_tutorial),
    path('iec_tutorial/', views.iec_tutorial),
    path('nec_cabletypes/', views.nec_cabletypes),
    path('iec_refmethods/', views.iec_refmethods),
    path('tech_notes/', views.tech_notes),
    path('troubleshooting/', views.troubleshooting),
]
