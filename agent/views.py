from django.shortcuts import render
from . import forms
from . import models

import os 
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Create your views here.


def homepage(request):
    result = None
    prompt = None
    # Initialize the form
    if request.method == 'POST':
        form = forms.PromptForm(request.POST)
        
        if form.is_valid():
            user_prompt = form.cleaned_data
            prompt = user_prompt.get('task')
            
            # Save the prompt to the database
            form.save()
            
            api_key = os.getenv('OPENROUTER_API_KEY')
            # Call the Allisson API
            response = requests.post(
                url = "https://openrouter.ai/api/v1/chat/completions",
                headers = {
                    "Authorization": api_key,
                    "Content-Type": 'application/json'
                },
                
                data = json.dumps({
                    'model': 'openai/gpt-4o-mini',
                    'messages': [{
                        'role': 'user',
                        'content': prompt
                    }],
                })
            )
            
            if response.status_code != 200:
                result = "Error: " + response.text
            result = response.json()['choices'][0]['message']['content']
    else:
        form = forms.PromptForm() 
    context = {
        'form': form,
        'prompt':prompt,
        'result': result 
    }
    
    return render(request, 'agent/home.html', context)



