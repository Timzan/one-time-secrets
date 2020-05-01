import asyncio
import logging
from typing import Dict
import motor.motor_asyncio as aiomotor
from aiohttp import web
from settings import config, init_mongo
from core.routes import setup_routes
from core.handler import MyHandler, error_middleware


async def setup_mongo(app: web.Application, conf: Dict, loop) -> aiomotor.AsyncIOMotorDatabase:
    mongo = await init_mongo(conf['mongo'], loop)

    async def close_mongo(app):
        mongo.client.close()

    app.on_cleanup.append(close_mongo)
    return mongo


async def init(loop):
    app = web.Application(middlewares=[error_middleware])

    mongo = await setup_mongo(app, config, loop)

    handler = MyHandler(mongo)
    setup_routes(app, handler)
    host, port = config['host'], config['port']

    return app, host, port


def main() -> None:

    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()

