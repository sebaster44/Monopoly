import json
import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from app.domain.errors import GameError
from app.rpc.protocol import (
    GAME_ERROR,
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    Message,
    Request,
    RpcError,
    error_message,
    result_message,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Method[Context]:
    params: type[BaseModel]
    handler: Callable[[Any, Context], Awaitable[BaseModel | None]]


class Dispatcher[Context]:
    def __init__(self, methods: Mapping[str, Method[Context]]) -> None:
        self._methods = methods

    async def handle(self, raw: str, context: Context) -> Message | None:
        """Process one incoming frame. Returns the response, or None for a notification."""
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return error_message(None, RpcError(PARSE_ERROR, "Parse error"))
        try:
            request = Request.model_validate(payload)
        except ValidationError:
            return error_message(None, RpcError(INVALID_REQUEST, "Invalid request"))

        try:
            response = result_message(request.id, await self._call(request, context))
        except RpcError as error:
            response = error_message(request.id, error)
        except GameError as error:
            response = error_message(request.id, RpcError(GAME_ERROR, str(error)))
        except Exception:
            logger.exception("Unexpected error while handling %s", request.method)
            response = error_message(request.id, RpcError(INTERNAL_ERROR, "Internal error"))
        return None if request.is_notification else response

    async def _call(self, request: Request, context: Context) -> Any:
        method = self._methods.get(request.method)
        if method is None:
            raise RpcError(METHOD_NOT_FOUND, f"Method not found: {request.method}")
        try:
            params = method.params.model_validate(request.params)
        except ValidationError as error:
            raise RpcError(INVALID_PARAMS, "Invalid params", _describe(error)) from error
        result = await method.handler(params, context)
        return None if result is None else result.model_dump(by_alias=True)


def _describe(error: ValidationError) -> list[dict[str, str]]:
    return [
        {"field": ".".join(str(part) for part in issue["loc"]), "message": issue["msg"]}
        for issue in error.errors()
    ]
