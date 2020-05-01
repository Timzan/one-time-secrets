from aiohttp.web import Application
from core.handler import MyHandler


def setup_routes(app: Application, handler: MyHandler) -> None:
    router = app.router
    router.add_route("*", "/generate", handler.generate, name='generate')
    router.add_route("*", "/secrets/{secret_key}", handler.return_secret, name='return_secret')
