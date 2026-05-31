import pytest

from diet.auth.constants import USERNAME_MAX_LENGTH
from diet.auth.models import User


def test_user_rejects_username_longer_than_max_length() -> None:
    with pytest.raises(
        ValueError,
        match=rf"Exceeds max length \({USERNAME_MAX_LENGTH} characters\)",
    ):
        User(
            username="a" * (USERNAME_MAX_LENGTH + 1),
            email="user@example.com",
        )
