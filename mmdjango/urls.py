from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'musicmatcher.views.home', name='home'),
    # url(r'^musicmatcher/', include('musicmatcher.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'mm.views.index'),
	url(r'^music$', 'mm.views.music'),
	url(r'^movies$', 'mm.views.movies'),
	url(r'^tv$', 'mm.views.tv'),
	url(r'^games$', 'mm.views.games'),
	url(r'^books$', 'mm.views.books'),
	url(r'^interests$', 'mm.views.interests'),
	url(r'^activities$', 'mm.views.activities'),
	url(r'^likes$', 'mm.views.likes'),
	
	url(r'^getcode$', 'mm.views.get_code'),
	
	url(r'^api$', 'mm.views.api'),
	url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DIR}),
)
