from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView   # ← ADD THIS

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # All API endpoints live under /api/
    path('api/', include('api.urls')),           # ← ADD THIS
    
    # Serve the React UI at the root URL "/"
    path('', TemplateView.as_view(template_name='index.html')),  # ← ADD THIS
]

