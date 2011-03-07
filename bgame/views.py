from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseNotFound
from django.template import RequestContext
from bgame.models import Game, Period, Player, ROLES
from bgame.forms import GameForm

import logging
log = logging.getLogger(__name__)

def index(request):
   games = Game.objects.all()
   return render_to_response('index.html', {'games': games, 'roles': ROLES, 'form': GameForm},
                                context_instance=RequestContext(request))

def game(request, game_slug, role):
    game_ = get_object_or_404(Game, game_slug=game_slug)
    player = get_object_or_404(Player, game__game_slug=game_slug, role=role)
    period = Period.objects.filter(player__game=game_).filter(player__role=role).order_by('-number')[0]

    return render_to_response('game.html', {'game': game, 'player': player,
                    'period': period}, context_instance=RequestContext(request))

def html(request):
    data = request.GET
    if 'template' in data:
        if data['template'] == 'game_listing':
            games = Game.objects.all()
            return render_to_response('game_listing.html', {'games': games, 'roles': ROLES,},
                                        context_instance=RequestContext(request))

        if data['template'] == 'period_listing':
            periods = Period.objects.filter(player__game__game_slug=data['game_slug']).filter(player__role=data['role']).exclude(number=0)
            print 'number of periods found: %d' % (periods.count(),)
            return render_to_response('period_listing.html', {'periods': periods}, context_instance=RequestContext(request))

    print 'template not in data'

    return HttpResponseNotFound()
