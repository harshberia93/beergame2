from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from bgame.models import Game, Period, Player, ROLES

import logging
log = logging.getLogger(__name__)

def index(request):
   games = Game.objects.all() 
   return render_to_response('index.html', {'games': games, 'roles': ROLES},
                                context_instance=RequestContext(request)) 

def game(request, game_slug, role):
    game_ = get_object_or_404(Game, game_slug=game_slug) 
    player = get_object_or_404(Player, game=game_, role=role) 
    period = get_object_or_404(Period, player__game=game_, player__role=role) 
    
    return render_to_response('game.html', {'game': game, 'player': player,
                    'period': period}, context_instance=RequestContext(request)) 
