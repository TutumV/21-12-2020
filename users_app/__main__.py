from aiohttp import web

from app import init_app


def main() -> None:
    app = init_app()
    web.run_app(app, host=app['config']['HOST'], port=app['config']['PORT'])


if __name__ == '__main__':
    main()
