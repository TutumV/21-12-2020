from aiohttp.web import Request, Response
from asyncpg.exceptions import UniqueViolationError
import logging

from middleware import login_required
from models import User, Token
from utils import CustomResponse, WebStatus, ErrorCode
from serializers import SignIn, SignUp

log = logging.getLogger(__name__)


async def sign_in(request: Request) -> Response:
    try:
        serializer_data = SignIn(**await request.json()).to_dict()
        user = await User.get(**serializer_data)
        token = await Token.create(user)
        return CustomResponse(web_status=WebStatus.OK,
                              code=ErrorCode.SUCCESS,
                              headers=dict(Token=token))
    except PermissionError:
        return CustomResponse(web_status=WebStatus.ERROR,
                              code=ErrorCode.NOT_FOUND)
    except (ValueError, TypeError) as error:
        log.error(error)
        return CustomResponse(web_status=WebStatus.ERROR,
                              code=ErrorCode.VALIDATION_ERROR)


async def sign_up(request: Request) -> Response:
    try:
        serializer_data = SignUp(**await request.json())
        await User.create(email=serializer_data.email,
                          password=serializer_data.password)
        return CustomResponse(web_status=WebStatus.OK,
                              code=ErrorCode.SUCCESS)
    except (ValueError, TypeError, UniqueViolationError) as error:
        log.error(error)
        return CustomResponse(web_status=WebStatus.ERROR,
                              code=ErrorCode.VALIDATION_ERROR)


@login_required
async def profile(request: Request) -> Response:
    return CustomResponse(web_status=WebStatus.OK,
                          data=request.user,
                          code=ErrorCode.SUCCESS)
