from django.db import models

# Create your models here.

class Prompt(models.Model):
    
    objective = models.TextField()
    task = models.TextField()

    def __str__(self):
        
        return f"Objective: {self.objective}, Task: {self.task}"

class Allisson(models.Model):
    
    name = models.CharField(max_length=40)
    tagline = models.CharField(max_length=150)
    description = models.TextField()
    objective = models.TextField()


    def __str__(self):
        
        print()
        
        return self.name

