from .base import *

DEBUG = False

ALLOWED_HOSTS = ["49.12.41.73"]

try:
    from .local import *
except ImportError:
    pass
