from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from datetime import datetime

# Help index page
def help(request):
    return render(request, "help/help.html")

def get_started(request):
    return render(request, "help/get_started.html")

def principles(request):
    return render(request, "help/principles.html")
    
def nec_tutorial(request):
    return render(request, "help/nec_tutorial.html")
    
def iec_tutorial(request):
    return render(request, "help/iec_tutorial.html")

def nec_cabletypes(request):
    return render(request, "help/nec_cabletypes.html")

def iec_refmethods(request):
    return render(request, "help/iec_refmethods.html")

def tech_notes(request):
    return render(request, "help/technotes.html")
    
# Troubleshooting page
def troubleshooting(request):  
    return render(request, 'help/faq.html')
