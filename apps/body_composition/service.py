import datetime
import json
import random
from datetime import timedelta

import pandas as pd
from pandas import DataFrame

from apps.body_composition.models import BodyComposition
from apps.body_composition.repository import BodyCompositionRepository
from apps.utils.custom_logger import CustomLogger

_logger = CustomLogger.get_logger()


class BodyCompositionService:
    @staticmethod
    def upsert(
        user_id: str, date: datetime.date, weight: float, body_fat: float
    ) -> None:
        _logger.info(f"Start: {user_id=}, {date=}, {weight=}, {body_fat=}")

        BodyCompositionRepository.upsert(user_id, date, weight, body_fat)

        _logger.info(f"End: {user_id=}, {date=}, {weight=}, {body_fat=}")

    @staticmethod
    def init_form_data(user_id: str) -> dict[str, float]:
        _logger.info(f"Start: {user_id=}")

        today = datetime.date.today()
        record = BodyCompositionRepository.get_by_user_and_date(user_id, today)
        if not record:
            record = BodyCompositionRepository.get_latest_by_user(user_id)

        form_data = {
            "weight": record.weight if record else 0.0,
            "body_fat": record.body_fat if record else 0.0,
        }

        _logger.info(f"End: {user_id=}, {form_data=}")
        return form_data

    @staticmethod
    def get_body_composition_dicts(
        user_id: str,
    ) -> list[dict[str, str | float]]:
        _logger.info(f"Start: {user_id=}")

        records = BodyCompositionRepository.get_body_compositions(user_id)
        if not records:
            _logger.info("Progress: Generate dummy data")
            dummy_date = datetime.date(1, 1, 1)
            records = [BodyComposition(dummy_date, 0.1)]

        dicts = BodyCompositionService._body_compositions_to_dicts(records)

        _logger.info(f"End: {user_id=}, {len(dicts)=}")
        return dicts

    @staticmethod
    def compute_monthly_statistics(
        body_composition_dicts: list[dict[str, str | float]],
    ) -> list[dict[str, float]]:
        _logger.info(f"Start: {len(body_composition_dicts)=}")

        body_composition_df = (
            BodyCompositionService._prepare_body_composition_dataframe(
                body_composition_dicts
            )
        )
        monthly_statistics_df = BodyCompositionService._compute_df(
            body_composition_df
        )
        monthly_statistics_json = BodyCompositionService._df_to_json(
            monthly_statistics_df
        )

        _logger.info(f"End: {len(monthly_statistics_json)=}")
        return monthly_statistics_json

    @staticmethod
    def generate_sample_data(
        duration_days: int = 365 * 3,
    ) -> list[dict[str, str | float]]:
        _logger.info(f"Start: {duration_days=}")

        today = datetime.datetime.today()
        past_date = today - timedelta(days=duration_days)
        date_pointer = past_date

        weight = round(random.uniform(90, 100), 2)
        body_fat = round(random.uniform(25, 30), 2)

        sample_data: list[dict[str, str | float]] = []
        while date_pointer <= today:
            weight_variation = round(random.uniform(-0.4, 0.36), 2)
            weight = round(max(weight + weight_variation, 50), 2)

            body_fat_variation = round(random.uniform(-0.2, 0.18), 2)
            body_fat = round(max(body_fat + body_fat_variation, 5), 2)

            sample_data.append(
                {
                    "date": date_pointer.strftime("%Y-%m-%d"),
                    "weight": weight,
                    "body_fat": body_fat,
                }
            )

            date_pointer += timedelta(days=1)

        _logger.info(f"End: {len(sample_data)=}")
        return sample_data

    @staticmethod
    def _prepare_body_composition_dataframe(
        body_composition_dicts: list[dict[str, str | float]]
    ) -> DataFrame:
        body_composition_df = pd.DataFrame(body_composition_dicts)
        body_composition_df["date"] = pd.to_datetime(
            body_composition_df["date"]
        )
        body_composition_df.set_index("date", inplace=True)
        return body_composition_df

    @staticmethod
    def _compute_df(
        body_composition_df: DataFrame,
    ) -> DataFrame:
        monthly_stats_df = body_composition_df.resample("ME").mean().round(2)

        monthly_stats_df["weight_change_rate"] = (
            (monthly_stats_df["weight"] - monthly_stats_df["weight"].shift(1))
            / monthly_stats_df["weight"].shift(1)
            * 100
        ).round(2)

        monthly_stats_df.reset_index(inplace=True)
        monthly_stats_df["date"] = monthly_stats_df["date"].dt.strftime(
            "%Y-%m"
        )

        return monthly_stats_df

    @staticmethod
    def _df_to_json(df: DataFrame) -> list[dict[str, float]]:
        str_json = df.to_json(orient="records")
        json_data = json.loads(str_json)
        return json_data

    @staticmethod
    def _body_compositions_to_dicts(
        body_compositions: list[BodyComposition],
    ) -> list[dict[str, str | float]]:
        return [
            {
                "date": body_composition.date.strftime("%Y-%m-%d"),
                "weight": body_composition.weight,
                "body_fat": body_composition.body_fat,
            }
            for body_composition in body_compositions
        ]
