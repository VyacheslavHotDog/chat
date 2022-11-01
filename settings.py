
from middleware.data_middleware import DataMiddleware

PLUGINS = ['plugins.common',]
MIDDLEWARE = [DataMiddleware]
JWT_SECRET = 'secret'

