from datetime import datetime
from django.db import IntegrityError
from django.core.exceptions import ValidationError
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
        attrs = request.data
        game = Game(group_name=attrs['group_name'],
                    num_periods=attrs['num_periods'])

        try:
            game.validate_unique()
        except ValidationError:
            resp = rc.BAD_REQUEST
            resp.content = 'Could not create game because name is not unique.'
            return resp

        try:
            game.clean_fields()
        except ValidationError as e:
            resp = rc.BAD_REQUEST
            resp.content = 'Invalid values for game.'
            return resp

        try:
            game.save()
        except:
            resp = rc.BAD_REQUEST
            resp.content = 'Unable to save game.'
            return resp

        return rc.CREATED

class PlayerHandler(AnonymousBaseHandler):
    model = Player
    fields = ( ('game', ('group_name', )), 'role', 'current_period', 'current_state', 'last_activity',)
    allowed_methods = ('GET', 'PUT',)

    def read(self, request, game_slug, role=None):
        base = Player.objects.all()

        base = base.filter(game__game_slug=game_slug)

        if base.count() == 0:
            resp = rc.NOT_FOUND
            resp.content = 'Could not find Players for "%s"' % (game_slug)
            return resp

        if role:
            try:
                base = base.get(role=role)
            except Period.DoesNotExist:
                resp = rc.NOT_FOUND
                resp.content = 'Could not find Player for "%s" with role %s' % (game_slug, role)
                return resp

        return base
    """
    @staticmethod
    def resource_uri(arg):
        print 'argument to static method: %s' % (arg,)
        return ('games',['id'])
    """

class PeriodHandler(AnonymousBaseHandler):
    model = Period
    fields = ('number', ('player', ('role', ('game', ('group_name',)) )), 'creation_time', 'completion_time', 'inventory',
                'backlog', 'demand', 'order_1', 'order_2', 'order_stash', 'shipment_1', 'shipment_2',
                'shipment_stash', 'shipped', 'order', 'current_cost', 'cumulative_cost',)
    allowed_methods = ('GET', 'POST', 'PUT',)

    def read(self, request, game_slug, role, number=None):
        base = Period.objects.all()

        base = base.filter(player__game__game_slug=game_slug)
        if base.count() == 0:
            resp = rc.NOT_FOUND
            resp.content = 'Could not find Periods for "%s"' % (game_slug,)
            return resp

        base = base.filter(player__role=role)
        if base.count() == 0:
            resp = rc.NOT_FOUND
            resp.content = 'Could not find Periods for "%s" in "%s"' % (role, game_slug)
            return resp

        if number:
            try:
                base = base.get(number=int(number))
            except Period.DoesNotExist:
                resp = rc.NOT_FOUND
                resp.content = 'Could not find Periods for "%s" in "%s" with number %d' % (role, game_slug, number)
                return resp

        return base

    def create(self, request):
        """
        Creates a Period object from POST.  This is the action
        associated with Start Game or Start Next Period button.
        """
        data = request.GET

        required_params = ('game_slug', 'role',)

        for param in required_params:
            if not param in data:
                log.debug('missing parameter "%s"' % (param))
                log.debug(data)
                resp = rc.BAD_REQUEST
                resp.content = 'Missing query parameter "%s"' % (param)
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
                        resp.content = 'Not allowed to create a period.'
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

    def update(self, request, game_slug, role):
        step = request.GET['step']
        if not step:
            resp = rc.BAD_REQUEST
            resp.content = 'Missing query parameter "step"'
            return resp

        def _get_current_period():
            period = Period.objects.filter(player__game__game_slug=game_slug)
            try:
                period.get(player__role=role)
            except Period.DoesNotExist:
                resp = rc.NOT_FOUND
                resp.content = 'Could not find period for "%s" in "%s"' % (role, game_slug)
                return resp

        def step1():
            """
            move shipment 2 to shipment 1, shipment 1 to inventory
            """

            period = _get_current_period()

            if not isinstance(period, Period):
                return period

        def step2():
            """
            move order 2 to order 1, order 1 to current order
            """
            pass

        def ship():
            """
            move shipment amount to downstream role
            """
            pass

        def order():
            """
            move order amount to upstream role
            """
            pass


        step_handler = {
            '1': step1,
            '2': step2,
            'ship': ship,
            'order': order,
        }

        return step_handler.get(step, lambda: rc.BAD_REQUEST)()
