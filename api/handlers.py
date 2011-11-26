from datetime import datetime
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, require_mime, require_extended

import logging

from beergame.bgame.models import Game, Player, Period, ROLES
from beergame.api.exceptions import InvalidStateChange, InvalidRole

log = logging.getLogger(__name__)

class GameHandler(AnonymousBaseHandler):
    model = Game
    fields = ('group_name', 'created', 'start_time', 'end_time', 'num_periods', 'archive')
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
#
# decorator -
#   requirements: first three arguments to decorated function must be
#                 request, game_slug, role
#
def update_last_activity(fn):
    def inner_func(*args, **kwargs):
        try:
            game_slug = kwargs['game_slug']
            role = kwargs['role']
        except:
            # TODO how to handle internal errors?
            pass

        try:
            player = Player.objects.filter(game__game_slug=game_slug).get(role=role)
        except Player.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.content = 'Could not find Player in "%s" with role "%s"' % (game_slug, role)
            return resp

        player.last_activity = datetime.now()
        player.save()

        print "updated last_activity"

        return fn(*args, **kwargs)
    return inner_func

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

    @update_last_activity
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

    @update_last_activity
    def create(self, request, game_slug, role):
        """
        Creates a Period object from POST.  This is the action
        associated with Start Game or Start Next Period button.
        """
        # check if other teams are in the currect states:
        #  + not_started: means teams haven't started
        players = Player.objects.filter(game__game_slug=game_slug)

        if players.count() == 0:
            resp = rc.NOT_FOUND
            resp.content = 'Could not find Players for "%s"' % (game_slug,)
            return resp

        try:
            player = players.get(role=role)
        except Player.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.content = 'Could not find Players in "%s" for "%s"' % (game_slug, role)
            return resp

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
        player.current_state = 'start'
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

    def _set_player_state(self, game_slug, role, state):
        """
        Can throw two exceptions
            * Player.DoesNotExist
            * InvalidStateChange (custom exception)
        """
        player = Player.objects.filter(game__game_slug=game_slug).get(role=role)

        current_state_index = [xx for xx, yy in enumerate(Player.STATES) if yy[0] == player.current_state][0]

        next_state_index = current_state_index + 1

        # if on order, the next state will be start (at index 1)
        if next_state_index == len(Player.STATES):
            next_state_index = 1

        next_state = Player.STATES[next_state_index][0]
        if next_state != state:
            raise InvalidStateChange('"%s" is not the next state after "%s" for player "%s" in "%s"' %\
                (state, player.current_state, player.role, player.game.game_slug))

        player.current_state = state
        player.save()

    @update_last_activity
    def update(self, request, game_slug, role, number):
        step = request.GET['step']
        if not step:
            resp = rc.BAD_REQUEST
            resp.content = 'Missing query parameter "step"'
            return resp

        def _get_current_period():
            period = Period.objects.filter(player__game__game_slug=game_slug)
            period = period.filter(player__role=role).order_by('-number')[0]
            return period

        def _get_upstream_player():
            """
            Can raise the following exception:
                * InvalidRole
            """
            try:
                role_index = [xx for xx, yy in enumerate(ROLES) if yy[0] == role][0]
            except KeyError as ex:
                raise InvalidRole('The role "%s" does not exist', (role,))

            if role_index != 0:
                upstream_role = ROLES[role_index - 1][0]
            else:
                raise InvalidRole('Should never ship to factory!')


            return Player.objects.filter(game__game_slug=game_slug).get(role=upstream_role)

        def _get_upstream_period():
            player = _get_upstream_player()
            # TODO make more robust
            return Period.objects.filter(player=player).get(number=number)

        def _get_downstream_player():
            """
            Can raise the following exception:
                * InvalidRole
            """
            try:
                role_index = [xx for xx, yy in enumerate(ROLES) if yy[0] == role][0]
            except KeyError as ex:
                raise InvalidRole('The role "%s" does not exist', (role,))

            if role_index != len(ROLES) - 1:
                downstream_role = ROLES[role_index + 1][0]
            else:
                raise InvalidRole('Should never order from retailer!')


            return Player.objects.filter(game__game_slug=game_slug).get(role=downstream_role)
        def _get_current_player():
            """
            Get current player object
            """
            return Player.objects.filter(game__game_slug=game_slug).get(role=role)

        def step1():
            """
            move shipment 2 to shipment 1, shipment 1 to inventory
            """

            period = _get_current_period()
            period.inventory += period.shipment_1
            period.shipment_1 = period.shipment_2

            if period.shipment_stash:
                period.shipment_2 = period.shipment_stash
                period.shipment_stash = None
            else:
                period.shipment_2 = None

            period.save()

            try:
                self._set_player_state(game_slug, role, 'step1')
            except Player.DoesNotExist as ex:
                resp = rc.NOT_FOUND
                resp.content = 'Could not find "%s" in "%s"' % (role, game_slug)
                return resp
            except InvalidStateChange as ex:
                resp = rc.BAD_REQUEST
                resp.content = ex.value
                return resp

            return rc.ALL_OK

        def step2():
            """
            move order 2 to order 1, order 1 to current order
            """

            period = _get_current_period()
            period.demand = period.order_1
            period.order_1 = period.order_2

            if period.order_stash:
                period.order_2 = period.order_stash
                period.order_stash = None
            else:
                period.order_2 = None

            period.save()

            try:
                self._set_player_state(game_slug, role, 'step2')
            except Player.DoesNotExist as ex:
                resp = rc.NOT_FOUND
                resp.content = 'Could not find "%s" in "%s"' % (role, game_slug)
                return resp
            except InvalidStateChange as ex:
                resp = rc.BAD_REQUEST
                resp.content = ex.value
                return resp

            return rc.ALL_OK

        def ship():
            """
            accept shipment from upstream player
            """
            try:
                upstream_player = _get_upstream_player()
                log.debug('shipping to upstream player: %s' % (upstream_player.role,))

            except Player.DoesNotExist as ex:
                resp = rc.BAD_REQUEST
                resp.content = 'Could not find upstream role for "%s"' % (role,)
                return resp

            if upstream_player.current_state != 'step2':
                resp = rc.BAD_REQUEST
                resp.content = 'Cannot ship when current state is "%s"' % (upstream_player.current_state,)
                return resp

            data = request.data
            period = _get_current_period()

            try:
                if period.shipment_2 is None:
                    period.shipment_2 = data['shipment_2']
                else:
                    period.shipment_stash = data['shipment_2']
                period.save()
            except KeyError as ex:
                resp = rc.BAD_REQUEST
                resp.content = 'Missing "shipment_2" in data'
                return resp

            # remove shipment from inventory
            up_period = _get_upstream_period()
            up_period.inventory -= int(data['shipment_2'])
            up_period.shipped = data['shipment_2']
            up_period.save()

            try:
                if role != 'retailer':
                    self._set_player_state(game_slug, upstream_player.role, 'ship')
                else:
                    self._set_player_state(game_slug, role, 'ship')
            except InvalidStateChange as ex:
                resp = rc.BAD_REQUEST
                resp.content = ex.value
                return resp

            return rc.ALL_OK

        def step3():
            player = _get_current_player()

            if player.current_state != 'ship':
                resp = rc.BAD_REQUEST
                resp.content = 'Cannot process Step 3 when current state is "%s"' % (player.current_state,)
                return resp

            player.current_state = 'step3'
            player.save()

            return rc.ALL_OK

        def order():
            """
            move order amount to upstream role
            """

            try:
                # the factory orders from itself
                if role == 'factory_self':
                    downstream_player = Player.objects.filter(game__game_slug=game_slug).get(role='factory')
                else:
                    downstream_player = _get_downstream_player()
            except Player.DoesNotExist as ex:
                resp = rc.BAD_REQUEST
                resp.content = 'Could not find downstream role for "%s"' % (role,)
                return resp

            if downstream_player.current_state != 'step3':
                resp = rc.BAD_REQUEST
                resp.content = 'Cannot order when current state is "%s"' % (downstream_player.current_state,)
                return resp

            data = request.data
            period = _get_current_period()

            try:
                if period.order_2 is None:
                    period.order_2 = data['order_2']
                else:
                    period.order_stash = data['order_2']
            except KeyError as ex:
                resp = rc.BAD_REQUEST
                resp.content = 'Missing "order_2" in data'
                return resp

            try:
                self._set_player_state(game_slug, downstream_player.role, 'order')
            except InvalidStateChange as ex:
                resp = rc.BAD_REQUEST
                resp.content = ex.value
                return resp

            return rc.ALL_OK

        step_handler = {
            '1': step1,
            '2': step2,
            'ship': ship,
            '3': step3,
            'order': order,
        }

        return step_handler.get(step, lambda: rc.BAD_REQUEST)()
