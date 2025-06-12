from django import forms
from django.core import validators

# form for searching a player
class PlayerSearchForm(forms.Form):
    player_name = forms.CharField(
        label='',
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Search a player',
                'class': 'form-control',
                'aria-label': 'Player Name'
            }
        ),
        error_messages={
            'required': 'Please enter a player name.',
            'max_length': 'Player name cannot exceed 100 characters.'
        }
    )