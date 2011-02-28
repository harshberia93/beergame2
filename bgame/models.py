from django.db import models
from django.template.defaultfilters import slugify

# roles for Player
ROLES = (
            ('factory','Factory'),
            ('distributor','Distributor'),
            ('wholesaler','Wholesaler'),
            ('retailer','Retailer')
        )


class Player(models.Model):
    """
    The Player models represents the individual Player in the Beer
    Game. They can be one of four roles: Factory, Distributor, Wholesaler,
    or Retailer.
    """
    game = models.ForeignKey('Game')
    role = models.CharField(max_length=11, choices=ROLES)
    current_period = models.IntegerField(default=0)
    STATES = (
                ('not_started','Not Started'),
                ('start','Start'),
                ('step1','Step 1'),
                ('step2','Step 2'),
                ('ship','Ship'),
                ('step3','Step 3'),
                ('order','Order'),
             )
    current_state = models.CharField(max_length=11, choices=STATES, default='not_started')
    last_activity = models.DateTimeField(null=True, blank=True)

    session = models.CharField(max_length=40, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Initializes the first Period for the Player
        """
        is_new = self.pk is None

        ret = super(Player, self).save(*args, **kwargs)

        if is_new:
            Period(player=self).save()

        return ret

    def __unicode__(self):
        return '%s playing in %s' % (self.role, self.game.name)


class Game(models.Model):
    """
    The Game model represents the collection of Players who are all
    part of the same supply chain. Each Player will participate in
    one of four roles: Factory, Distributor, Wholesaler, or Retailer.
    """
    group_name = models.CharField(max_length=40, unique=True)
    game_slug = models.SlugField(unique=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(blank=True, null=True)
    num_periods = models.IntegerField(default=30, verbose_name='Number of periods')
    archive = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Creates a Player for each role in the supply chain
        """
        is_new = self.pk is None

        self.game_slug = slugify(self.group_name)

        super(Game, self).save(*args, **kwargs)

        if is_new:
            for role in ROLES:
                Player(role=role[0], game=self).save()


    def __unicode__(self):
        return '%s' % (self.group_name)


class Period(models.Model):
    """
    The Period model stores the state of the game for the current
    period.  Each Player has his own Period.  When the Player is first
    created, they have a 0 Period that contains the default game setup.
    """
    number = models.IntegerField(default=0)
    player = models.ForeignKey(Player)

    creation_time = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField(null=True, blank=True)

    inventory = models.IntegerField(default=12)
    backlog = models.IntegerField(default=0)

    # demand is the order for the current period
    demand = models.IntegerField(blank=True, null=True)
    order_1 = models.IntegerField(blank=True, null=True, default=4)
    order_2 = models.IntegerField(blank=True, null=True, default=4)

    # stashes order if Player has not advanced order_2 to order_1
    order_stash = models.IntegerField(blank=True, null=True)

    shipment_1 = models.IntegerField(blank=True, null=True, default=4)
    shipment_2 = models.IntegerField(blank=True, null=True, default=4)

    # stashes shipment if Player hasn't moved shipment_2 to shipment_1
    shipment_stash = models.IntegerField(blank=True, null=True)

    shipped = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, default=0)

    current_cost = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    cumulative_cost = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')

    def __unicode__(self):
        return '%d / %s / %s' % (self.number, self.team.role, self.team.game.name)
