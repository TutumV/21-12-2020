from aiohttp import web
import sys
import logging

from utils import AccessLogger, LogstashFormatter
from middleware import auth_middleware
from models import migrate
from urls import init_routes
from database import Database
from settings import Config


log = logging.getLogger()
console = logging.StreamHandler(sys.stdout)
console.setFormatter(LogstashFormatter())
console.setLevel(logging.INFO)
log.addHandler(console)
log.setLevel(logging.INFO)


async def init_database(app: web.Application) -> None:
    user = app['config'].DB_USER
    password = app['config'].DB_PASSWORD
    host = app['config'].DB_HOST
    port = app['config'].DB_PORT
    db = app['config'].DATABASE
    dsn = f"postgres://{user}:{password}@{host}:{port}/{db}"
    await Database.connect(dsn)
    log.info(f'start database pool with dsn {dsn}')
    await migrate()


async def close_database(app: web.Application) -> None:
    await Database.pool.close()


def setup_middleware(app: web.Application) -> None:
    app.middlewares.append(auth_middleware)


def init_app() -> web.Application:
    app = web.Application(handler_args={"access_log_class": AccessLogger})

    app['config'] = Config
    print(app['config'].HOST)
    init_routes(app)
    setup_middleware(app)
    app.on_startup.extend([init_database, ])
    app.on_cleanup.extend([close_database, ])

    return app

