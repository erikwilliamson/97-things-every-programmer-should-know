# 3rd-Party Imports
from starlette.datastructures import Headers
from starlette.requests import Request


def starlette_request(
    method: str = "GET",
    server: str = "www.example.com",
    path: str = "/",
    headers: dict = None,
    body: str = None,
) -> Request:
    if headers is None:
        headers = {}
    request = Request(
        {
            "type": "http",
            "path": path,
            "headers": Headers(headers).raw,
            "http_version": "1.1",
            "method": method,
            "scheme": "https",
            "client": ("127.0.0.1", 8080),
            "server": (server, 443),
        }
    )
    if body:

        async def request_body():
            return body

        request.body = request_body

    return request
