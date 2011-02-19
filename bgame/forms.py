from django.forms import ModelForm
from bgame.models import Game 

class GameForm(ModelForm):
    class Meta:
        model = Game 
