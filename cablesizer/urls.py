from django.urls import path, include

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    path('', include('common.urls')),
    # Examples:
    # url(r'^$', 'myproject.views.home', name='home'),
    # url(r'^myproject/', include('myproject.foo.urls')),

    #(r'^upgrade/', 'myproject.common.views.upgrade'),
    #(r'^feedback/', 'myproject.common.views.feedback'),

    path('iec/', include('sizer.urls')),
    path('nec/', include('nec.urls')),
    path('help/', include('help.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
