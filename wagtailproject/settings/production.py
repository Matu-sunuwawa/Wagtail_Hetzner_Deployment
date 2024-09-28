from .base import *

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-o*8e$l2h4fvz=f^zi=yac3+oak&xt%!re2sn463c(9#jbk(2ju"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["49.12.41.73"]

try:
    from .local import *
except ImportError:
    pass
