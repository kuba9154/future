from django.conf.urls.defaults import patterns, include, url
from django.http import HttpResponse
from futureapp.views import post 

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^post/$',post),
    url(r'^home/$', 'django.views.generic.simple.direct_to_template', {'template': 'future/static2.html'})
    # Examples:
    # url(r'^$', 'future.views.home', name='home'),
    # url(r'^future/', include('future.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
