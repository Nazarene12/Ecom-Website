from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from channels.routing import ProtocolTypeRouter , URLRouter

from Ecom_Web.routing import websocket_urlpatterns





application = ProtocolTypeRouter({
     'websocket':#AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    # )
})