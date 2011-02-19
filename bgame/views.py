from django.shortcuts import render_to_response
from django.template import RequestContext
from bgame.models import Game

def index(request):
   games = Game.objects.all() 
   return render_to_response('index.html', {'games': games},
                                context_instance=RequestContext(request)) 
