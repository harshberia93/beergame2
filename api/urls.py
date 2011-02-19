from django.conf.urls.defaults import patterns, include, url
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.doc import documentation_view

from beergame.api.handlers import GameHandler, PlayerHandler, PeriodHandler

games = Resource(handler=GameHandler)
players = Resource(handler=PlayerHandler)
periods = Resource(handler=PeriodHandler)

#import pdb; pdb.set_trace()

urlpatterns = patterns('',
    (r'^games/$', games),
    (r'^games/(?P<emitter_format>.+)/$', games),

    (r'^players/$', players),
    (r'^players/(?P<emitter_format>.+)/$', players),

    (r'^periods/$', periods),
    (r'^periods/(?P<emitter_format>.+)/$', periods),

    url(r'^$', documentation_view),
)
