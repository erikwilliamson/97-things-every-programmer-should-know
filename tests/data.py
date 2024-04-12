"""
Test data handlers
"""

# Standard Library Imports
from datetime import datetime, timezone


async def add_test_user() -> None:
    """Adds test users to user collection"""
    test_user = User(
        email="test@test.io",
        hashed_password=hash_password("test@test.io"),
        full_name="Test User",
        email_confirmed_at=datetime.now(tz=timezone.utc),
        disabled=False,
        role="musician",
        phone_number="+1 (888) 555-1212",
    )
    await test_user.create()
