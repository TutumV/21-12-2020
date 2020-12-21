from aiohttp.web import Application

from views import sign_in, profile, sign_up


def init_routes(app: Application) -> None:
    add_route = app.router.add_route

    add_route('POST', '/sign-in', sign_in, name='sign_in')
    add_route('GET', '/profile', profile, name='profile')
    add_route('POST', '/sign-up', sign_up, name='sign_up')
