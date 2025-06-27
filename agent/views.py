from django.shortcuts import render
from . import forms
from . import models

import os 
import time
import requests
import json
from dotenv import load_dotenv
import markdown  # NEW: For converting markdown to HTML

load_dotenv()

# Create your views here.


def homepage(request):
    result = None
    prompt = None
    # Get all previous prompts and responses for chat history
    conversation = models.Prompt.objects.all()  # You can filter by user/session if needed
    
    # Initialize the form
    if request.method == 'POST':
        form = forms.PromptForm(request.POST)
        
        if form.is_valid():
            user_prompt = form.cleaned_data
            task_prompt = user_prompt.get('task')
            
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
                        'content': task_prompt
                    }],
                })
            )
            
            if response.status_code != 200:
                result = "Error: " + response.text
            else:
                raw_result = response.json()['choices'][0]['message']['content']
                # NEW: Convert markdown to HTML for better formatting
                result = markdown.markdown(raw_result, extensions=['extra', 'nl2br'])
                
            # Saving both prompt and response to the database
            prompt_obj = form.save(commit=False)
            prompt_obj.response = result  # Attaching the AI response as HTML
            prompt_obj.save()  
            # Refresh conversation 
            conversation = models.Prompt.objects.all()
    else:
        form = forms.PromptForm() 
    context = {
        'form': form,
        'prompt':prompt,
        'result': result,
        'conversation': conversation  # Chat History
    }
    
    return render(request, 'agent/home.html', context)



