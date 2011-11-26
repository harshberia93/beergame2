from django.contrib import admin
from beergame.bgame.models import Player, Game, Period

class PlayerAdmin(admin.ModelAdmin):
    pass

class GameAdmin(admin.ModelAdmin):
    pass

class PeriodAdmin(admin.ModelAdmin):
    pass

admin.site.register(Player, PlayerAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Period, PeriodAdmin)
