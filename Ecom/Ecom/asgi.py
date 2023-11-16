"""
ASGI config for Ecom project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# import os
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter , URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# from django.core.asgi import get_asgi_application


# import Ecom_Web.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecom.settings')

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#     # 'http':django_asgi_app,

#     'websocket':AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter(
#                 Ecom_Web.routing.websocket_urlpatterns
#             )
#         ),
#     )
# })

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecom.settings')

application = get_asgi_application()

