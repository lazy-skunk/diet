import datetime
import json
import random
from typing import Any

import pandas as pd
from flask import Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required
from pandas import DataFrame
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response

from apps.body_composition.models import BodyComposition
from apps.extensions import sql_alchemy
from apps.utils.singleton_logger import SingletonLogger

_logger = SingletonLogger.get_logger()


class BodyCompositionService:
    @classmethod
    def upsert(
        cls, user_id: str, date: datetime.date, weight: float, body_fat: float
    ) -> None:
        _logger.info("Starting body composition data upsert.")

        specified_date_record: BodyComposition = (
            BodyComposition.query.filter_by(date=date, user_id=user_id).first()
        )

        if specified_date_record:
            specified_date_record.weight = weight
            specified_date_record.body_fat = body_fat
        else:
            new_log = BodyComposition(
                date=date,
                weight=weight,
                body_fat=body_fat,
                user_id=user_id,
            )
            sql_alchemy.session.add(new_log)

        try:
            sql_alchemy.session.commit()
            _logger.info(
                "Body composition data upsert completed successfully."
            )
        except SQLAlchemyError:
            sql_alchemy.session.rollback()
            _logger.error(
                "Body composition data upsert failed due to database error.",
                exc_info=True,
            )
            raise

    @classmethod
    def init_form_data(cls, user_id: str) -> dict[str, float]:
        _logger.info("Starting form data initialization.")

        today = datetime.date.today()
        form_data = {"weight": 0.0, "body_fat": 0.0}

        todays_record: BodyComposition = BodyComposition.query.filter_by(
            date=today, user_id=user_id
        ).first()
        if todays_record:
            form_data["weight"] = todays_record.weight
            form_data["body_fat"] = todays_record.body_fat
            _logger.info(
                "Form data initialization completed successfully"
                " with today's record."
            )
            return form_data

        last_registered_record: BodyComposition = (
            BodyComposition.query.filter_by(user_id=user_id)
            .order_by(BodyComposition.date.desc())
            .first()
        )
        if last_registered_record:
            form_data["weight"] = last_registered_record.weight
            form_data["body_fat"] = last_registered_record.body_fat
            _logger.info(
                "Form data initialization completed successfully"
                " with last registered record."
            )
            return form_data

        _logger.info(
            "Form data initialization completed successfully"
            " with default values."
        )
        return form_data
