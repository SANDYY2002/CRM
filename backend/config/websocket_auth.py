from urllib.parse import parse_qs

from channels.db import close_old_connections
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        scope["user"] = AnonymousUser()
        query = parse_qs(scope.get("query_string", b"").decode())
        token_values = query.get("token", [])
        if token_values:
            try:
                jwt = JWTAuthentication()
                validated = jwt.get_validated_token(token_values[0])
                scope["user"] = await jwt.get_user(validated)
            except Exception:
                scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)
