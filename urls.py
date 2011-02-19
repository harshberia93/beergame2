from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beergame.views.home', name='home'),
    # url(r'^beergame/', include('beergame.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('beergame.bgame.urls')),
    url(r'^b/', include('beergame.bgame.urls')),
    url(r'^api/', include('beergame.api.urls')),
)
