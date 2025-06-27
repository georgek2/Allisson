from . import models 
from django.forms import ModelForm

class PromptForm(ModelForm):
    class Meta:
        model = models.Prompt
        # Only show the 'task' field in the form for user input (objective/response are not needed from user)
        fields = ['objective', 'task']  # UPDATED: Only show the prompt input field