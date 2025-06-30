
import os 
import json
import requests
from dotenv import load_dotenv 

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')

# Allisson - Leader 
def allisson(prompt: str):
    
    # Talk to Allisson
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
    pass 

def fiona(prompt: str):
    
    # Talk to Fiona
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
    
    pass 

def lisa(prompt: str):
    
    # Talk to Lisa
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
    
    pass 

def ben(prompt: str):
    
    # Talk to Ben
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
    
    pass 

