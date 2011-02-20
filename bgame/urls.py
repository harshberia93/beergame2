from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beergame.views.home', name='home'),
    # url(r'^beergame/', include('beergame.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
#    (r'^$', direct_to_template, {'template': 'index.html'}),
    url(r'^(?P<game_slug>[^/]+)/(?P<role>factory|distributor|wholesaler|retailer)$', 'bgame.views.game', name='game'), 
    url(r'^html/$', 'bgame.views.html', name='html'), 
)
