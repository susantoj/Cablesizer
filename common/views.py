from datetime import datetime
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import render

from sizer.models import EmailList


# Index page (redirect)
def index(request):
    return render(request, 'home.htm')

# Help page
def help(request):  
    return render(request, 'help/help.html')

# About page
def about(request):  
    return render(request, 'about.html')

# Feedback page
def feedback(request):  
    c = {}
    c.update(csrf(request))
    
    if (request.method == 'POST'):
        send_mail('Cablesizer Feedback', request.POST.get('feedback_text', ''), 'feedback@cablesizer.com',
    ['julius.susanto@gmail.com'], fail_silently=True)
        show_message = 1
    
    return render(request, 'feedback.html', locals())
    
# Upgrade page
def upgrade(request):
    c = {}
    c.update(csrf(request))
    
    if (request.method == 'POST'):
        email_query = request.POST.get('email_address', '')
        email_add = EmailList(email_address=email_query, date=datetime.now())
        email_add.save()
        show_message = 1
    
    return render(request, 'upgrade.html', locals())
    
# Disclaimer page
def disclaimer(request):  
    return render(request, 'disclaimer.html')

# New cable page
def new(request):
    if (request.method == 'GET'):
        request.session.clear()

        request.session["volts"] = 400
        request.session["load_kw"] = 30
        request.session["pf"] = 0.8
        request.session["eff"] = 0.9
    return render(request, 'new.html')