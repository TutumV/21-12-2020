from aiohttp import web
import jwt

from utils import CustomResponse, WebStatus, ErrorCode
from settings import Config


def login_required(func):
    async def wrapper(request):
        if not request.user:
            return CustomResponse(web_status=WebStatus.ERROR,
                                  code=ErrorCode.CREDENTIALS_ERROR)
        return await func(request)
    return wrapper


@web.middleware
async def auth_middleware(request, handler):
    request.user = None
    token = request.headers.get('token', None)
    if token:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY,
                             algorithms=[Config.JWT_ALGORITHM])
        payload.pop('time')
        request.user = payload
    return await handler(request)
