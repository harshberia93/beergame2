from datetime import datetime
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, require_mime, require_extended

import logging

from beergame.bgame.models import Game, Player, Period

log = logging.getLogger(__name__)

class GameHandler(AnonymousBaseHandler):
    model = Game
    fields = ('group_name', 'created', 'start_time', 
                'end_time', 'num_periods', 'archive') 
    allowed_methods = ('GET', 'POST',)

    def read(self, request, group_name=None):
        base = Game.objects

        if group_name:
            return base.get(group_name=group_name)
        return base.all()

    def create(self, request):
        print request.content_type
        print request.data
        attrs = request.data
        game = Game(group_name=attrs['group_name'],
                    num_periods=attrs['num_periods']) 
        game.save()
        
        resp = rc.CREATED 
        return rc.CREATED 

class PlayerHandler(AnonymousBaseHandler):
    model = Player
    fields = ( ('game', ('group_name', )), 'role', 'current_period', 'current_state', 'last_activity',) 
    allowed_methods = ('GET', 'PUT',)

    def read(self, request):
        base = Player.objects

        return base.all()

class PeriodHandler(AnonymousBaseHandler):
    model = Period
    fields = ('number', ('player', ('role', ('game', ('group_name',)) )), 'creation_time', 'completion_time', 'inventory',
                'backlog', 'demand', 'order_1', 'order_2', 'order_stash', 'shipment_1', 'shipment_2',
                'shipment_stash', 'shipped', 'order', 'current_cost', 'cumulative_cost',)
    allowed_methods = ('GET', 'POST', 'PUT',)

    def read(self, request):
        base = Period.objects.all()
        
        if 'game_slug' in request.GET:
            base = base.filter(player__game__game_slug=request.GET['game_slug'])
        if 'role' in request.GET:
            base = base.filter(player__role=request.GET['role'])
            
        return base 

    def create(self, request):
        data = request.GET

        required_params = ('game_slug', 'role',)

        for param in required_params:
            if not param in data:
                log.debug('missing parameter "%s"' % (param))
                log.debug(data)
                resp = rc.BAD_REQUEST
                resp.write('Missing query parameter "%s"' % (param))
                return resp 

        game_slug = data['game_slug']
        role = data['role']

        # check if other teams are in the currect states: 
        #  + not_started: means teams haven't started
        players = Player.objects.filter(game__game_slug=game_slug)

        player = players.get(role=role)
        cur_period = player.current_period + 1

        other_players = players.exclude(role=role)
        for o_player in other_players:
            if player.current_period != 0: 
                if not o_player.current_period == cur_period:
                    if o_player.current_state != 'order':
                        resp = rc.BAD_REQUEST
                        resp.write('Not allowed to create a period.') 
                        return resp 

        # increment the period
        player = players.get(role=role)
        player.current_period = cur_period
        player.save()

        o_per = Period.objects.filter(player__game__game_slug=game_slug)
        o_per = o_per.filter(player__role=role).order_by('-number')[0]
        o_per.completion_time = datetime.now()
        o_per.save()

        n_per = Period(number=cur_period, player=o_per.player, inventory=o_per.inventory,
            backlog=o_per.backlog, order_1=o_per.order_1, order_2=o_per.order_2,
            shipment_1=o_per.shipment_1, shipment_2=o_per.shipment_2, 
            cumulative_cost=o_per.current_cost+o_per.cumulative_cost)
        n_per.save()

        return rc.CREATED
