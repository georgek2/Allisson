from . import models 
from django.forms import ModelForm

class PromptForm(ModelForm):
    
    class Meta:
        model = models.Prompt
        fields = '__all__'