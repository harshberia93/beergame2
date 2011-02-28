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
    (r'^games/(?P<group_name>[^/]+)/$', games),

    (r'^games/(?P<game_slug>[^/]+)/players/$', players),
    (r'^games/(?P<game_slug>[^/]+)/players/(?P<role>[^/]+)/$', players),

    (r'^games/(?P<game_slug>[^/]+)/players/(?P<role>[^/]+)/periods/$', periods),
    (r'^games/(?P<game_slug>[^/]+)/players/(?P<role>[^/]+)/periods/(?P<number>\d+)/$', periods),

    url(r'^$', documentation_view),
)
