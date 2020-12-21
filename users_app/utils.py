from aiohttp.web import Response
import json
from enum import Enum
from json import dumps
from aiohttp.abc import AbstractAccessLogger
import traceback
import logging
from datetime import datetime


class WebStatus:
    OK = 'ok'
    ERROR = 'error'


class ErrorCode(Enum):
    SUCCESS = 0
    VALIDATION_ERROR = 1
    UNEXPECTED_ERROR = 2
    CREDENTIALS_ERROR = 3
    NOT_FOUND = 4


class CustomResponse(Response):
    def __init__(self, web_status: WebStatus, code: ErrorCode, data=None, headers=None):
        response_data = {
            "status": web_status,
            'data': data if data else dict(),
            "errors": {
                "code": code.value,
                "message": code.name,
            },
        }
        super().__init__(
            text=dumps(response_data),
            content_type='application/json',
            headers=headers if headers else dict()
        )


class AccessLogger(AbstractAccessLogger):
    @staticmethod
    def multidict_to_dict(mdict):
        result = {}
        for (key, value) in mdict.items():
            key = key.lower()
            if key == "authorization":
                continue
            if key not in result:
                result[key] = value
        return result

    def log(self, request, response, time):
        self.logger.info(
            "%s %s",
            request.method,
            request.url,
            extra={
                "request": {
                    "method": request.method,
                    "path": request.path,
                    "remote": request.remote,
                    "query": AccessLogger.multidict_to_dict(request.query),
                    "headers": AccessLogger.multidict_to_dict(request.headers),
                },
                "response": {
                    "status": response.status,
                    "reason": response.reason,
                    "headers": AccessLogger.multidict_to_dict(response.headers),
                },
                "process_time": time,
            },
        )


class LogstashFormatter(logging.Formatter):
    def __init__(self, message_type="Logstash"):
        super().__init__()
        self.message_type = message_type

    def get_extra_fields(self, record):
        skip_list = (
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "id",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "extra",
            "auth_token",
            "password",
            "stack_info",
        )

        easy_types = (str, bool, dict, float, int, list, type(None))
        fields = {}

        for key, value in record.__dict__.items():
            if key not in skip_list:
                if isinstance(value, easy_types):
                    fields[key] = value
                else:
                    fields[key] = repr(value)

        return fields

    def get_debug_fields(self, record):
        fields = {
            "stack_trace": self.format_exception(record.exc_info),
            "lineno": record.lineno,
            "process": record.process,
            "thread_name": record.threadName,
        }

        if not getattr(record, "funcName", None):
            fields["funcName"] = record.funcName

        if not getattr(record, "processName", None):
            fields["processName"] = record.processName

        return fields

    @classmethod
    def format_source(cls, message_type, host, path):
        return "%s://%s/%s" % (message_type, host, path)

    @classmethod
    def format_timestamp(cls, time):
        tstamp = datetime.utcfromtimestamp(time)
        return (
                tstamp.strftime("%Y-%m-%dT%H:%M:%S")
                + ".%03d" % (tstamp.microsecond / 1000)
                + "Z"
        )

    @classmethod
    def format_exception(cls, exc_info):
        return "".join(
            traceback.format_exception(*exc_info)) if exc_info else ""

    @classmethod
    def serialize(cls, message):
        return json.dumps(message, indent=2)

    def format(self, record):
        message = {
            "@timestamp": self.format_timestamp(record.created),
            "level": record.levelname,
            "message": record.getMessage(),
            "path": record.pathname,
            "type": self.message_type,
            "logger_name": record.name,
        }

        message.update(self.get_extra_fields(record))

        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)