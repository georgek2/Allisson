import os

# Default to dev settings
env = os.getenv('DJANGO_ENV', 'dev')

if env == 'prod':
    from .prod import *
else:
    from .dev import *