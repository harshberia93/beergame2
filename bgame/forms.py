from django.forms import ModelForm
from bgame.models import Game 

class GameForm(ModelForm):
    class Meta:
        model = Game 
        exclude = ('game_slug', 'start_time', 'end_time', 'archive')
