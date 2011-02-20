from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beergame.views.home', name='home'),
    # url(r'^beergame/', include('beergame.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'beergame.bgame.views.index', name='index'),
    url(r'^g/', include('beergame.bgame.urls')),
    url(r'^api/', include('beergame.api.urls')),
)
