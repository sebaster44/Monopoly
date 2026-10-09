"""JSON-RPC 2.0 message shapes (https://www.jsonrpc.org/specification)."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
# Implementation-defined server error range starts at -32000.
GAME_ERROR = -32000

type RequestId = int | str | None
type Message = dict[str, Any]


class RpcError(Exception):
    def __init__(self, code: int, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"]
    method: str
    # Only named parameters are supported.
    params: dict[str, Any] = Field(default_factory=dict)
    id: RequestId = None

    @property
    def is_notification(self) -> bool:
        return "id" not in self.model_fields_set


def result_message(request_id: RequestId, result: Any) -> Message:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_message(request_id: RequestId, error: RpcError) -> Message:
    body: Message = {"code": error.code, "message": error.message}
    if error.data is not None:
        body["data"] = error.data
    return {"jsonrpc": "2.0", "id": request_id, "error": body}


def notification_message(method: str, params: Message) -> Message:
    return {"jsonrpc": "2.0", "method": method, "params": params}
