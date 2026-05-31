import datetime
from collections.abc import Callable

import pytest
from sqlalchemy.exc import IntegrityError

from diet.auth.models import User
from diet.body_composition.models import BodyComposition
from diet.extensions import sql_alchemy


def test_body_composition_user_date_must_be_unique(
    create_user: Callable[..., User],
) -> None:
    user = create_user()

    first_record = BodyComposition(
        user_id=user.id,
        date=datetime.date(2026, 5, 31),
        weight=70.0,
        body_fat=20.0,
    )
    duplicate_record = BodyComposition(
        user_id=user.id,
        date=datetime.date(2026, 5, 31),
        weight=71.0,
        body_fat=19.5,
    )

    sql_alchemy.session.add_all([first_record, duplicate_record])

    with pytest.raises(IntegrityError):
        sql_alchemy.session.commit()
