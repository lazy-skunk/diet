import datetime
import json

import pandas as pd
from pandas import DataFrame

from diet.body_composition.models import BodyComposition
from diet.body_composition.repository import (
    get_body_compositions,
    get_by_user_and_date,
    get_latest_by_user,
    upsert,
)
from diet.utils.custom_logger import get_logger
from diet.utils.transaction import commit

_logger = get_logger()


def upsert_body_composition(
    user_id: int, date: datetime.date, weight: float, body_fat: float | None
) -> None:
    _logger.info(f"Start: {user_id=}, {date=}, {weight=}, {body_fat=}")
    upsert(user_id, date, weight, body_fat)
    commit()
    _logger.info(f"End: {user_id=}, {date=}, {weight=}, {body_fat=}")


def init_form_data(user_id: int) -> dict[str, float | None]:
    _logger.info(f"Start: {user_id=}")

    today = datetime.date.today()
    record = get_by_user_and_date(user_id, today)
    if not record:
        record = get_latest_by_user(user_id)

    form_data = {
        "weight": record.weight if record else 0.0,
        "body_fat": record.body_fat if record else 0.0,
    }

    _logger.info(f"End: {user_id=}, {form_data=}")
    return form_data


def get_body_composition_dicts(
    user_id: int,
) -> list[dict[str, str | float | None]]:
    _logger.info(f"Start: {user_id=}")

    records = get_body_compositions(user_id)
    data = _body_compositions_to_dicts(records)

    _logger.info(f"End: {user_id=}, {len(data)=}")
    return data


def compute_monthly_statistics(
    body_composition_dicts: list[dict[str, str | float | None]],
) -> list[dict[str, str | float | None]]:
    _logger.info(f"Start: {len(body_composition_dicts)=}")

    if not body_composition_dicts:
        _logger.info("End: no data")
        return []

    body_composition_df = _prepare_body_composition_dataframe(
        body_composition_dicts
    )
    monthly_statistics_df = _compute_df(body_composition_df)
    monthly_statistics_json = _df_to_json(monthly_statistics_df)

    _logger.info(f"End: {len(monthly_statistics_json)=}")
    return monthly_statistics_json


def _prepare_body_composition_dataframe(
    body_composition_dicts: list[dict[str, str | float | None]],
) -> DataFrame:
    body_composition_df = pd.DataFrame(body_composition_dicts)
    body_composition_df["date"] = pd.to_datetime(body_composition_df["date"])
    body_composition_df.set_index("date", inplace=True)
    return body_composition_df


def _compute_df(body_composition_df: DataFrame) -> DataFrame:
    monthly_stats_df = body_composition_df.resample("ME").mean().round(2)

    monthly_stats_df["weight_change_rate"] = (
        (monthly_stats_df["weight"] - monthly_stats_df["weight"].shift(1))
        / monthly_stats_df["weight"].shift(1)
        * 100
    ).round(2)

    monthly_stats_df.reset_index(inplace=True)
    monthly_stats_df["date"] = monthly_stats_df["date"].dt.strftime("%Y-%m")

    return monthly_stats_df


def _df_to_json(df: DataFrame) -> list[dict[str, str | float | None]]:
    str_json = df.to_json(orient="records")
    json_data = json.loads(str_json)
    return json_data


def _body_compositions_to_dicts(
    body_compositions: list[BodyComposition],
) -> list[dict[str, str | float | None]]:
    return [
        {
            "date": body_composition.date.strftime("%Y-%m-%d"),
            "weight": body_composition.weight,
            "body_fat": body_composition.body_fat,
        }
        for body_composition in body_compositions
    ]
