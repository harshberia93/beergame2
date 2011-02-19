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
        base = Period.objects

        return base.all()
