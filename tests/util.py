"""
Common test utilities
"""

# Standard Library Imports
import random
import string

# 3rd-Party Imports
#
from async_asgi_testclient import TestClient

#
# from ninety_seven_things.lib.models.auth import RefreshToken
#
#
# async def auth_payload(client: TestClient, email: str) -> RefreshToken:
#     """Returns the login auth payload for an email"""
#     data = {"email": email, "password": email}
#     resp = await client.post("/auth/login", json_payloads=data)
#     return RefreshToken(**resp.json_payloads())
#
#
# async def auth_headers(client: TestClient, email: str) -> dict[str, str]:
#     """Returns the authorization headers for an email"""
#     auth = await auth_payload(client, email)
#     return {"AUTHORIZATION": f"Bearer {auth.access_token}"}


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"
