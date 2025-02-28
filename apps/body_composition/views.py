import json
import random
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from pandas import DataFrame
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response

from apps.body_composition.services.body_composition_service import (
    BodyCompositionService,
)
from apps.extensions import sql_alchemy

from .forms import RecordBodyCompositionForm
from .models import BodyComposition

blueprint = Blueprint(
    "body_composition",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/body_composition",
)


@blueprint.route("/record_body_composition", methods=["GET", "POST"])
@login_required
def record_body_composition() -> str | Response:
    user_id = current_user.id
    form = RecordBodyCompositionForm()

    if request.method == "GET":
        form_data = BodyCompositionService.init_form_data(user_id)
        form.weight.data = form_data["weight"]
        form.body_fat.data = form_data["body_fat"]
        return render_template(
            "body_composition/record_body_composition.html", form=form
        )

    if form.validate_on_submit():
        input_date = form.date.data
        weight = form.weight.data
        body_fat = form.body_fat.data

        try:
            BodyCompositionService.upsert(
                user_id, input_date, weight, body_fat
            )
            flash("Body composition data saved successfully.", "success")
            return redirect(url_for("main.index"))
        except (ValueError, TypeError) as e:
            flash(str(e), "danger")
        except SQLAlchemyError:
            flash(
                "Body composition record failed. Please try again later.",
                "danger",
            )

    return render_template(
        "body_composition/record_body_composition.html", form=form
    )


# TODO: 循環的複雑度が高い。
# TODO: views が MVC でいう controller だとしたら肥大化しすぎている。
@blueprint.route("/get_body_composition_data", methods=["GET"])
def fetch_body_composition_data() -> Response:
    def _get_body_compositions(user_id: str) -> list:
        body_composition_objects = (
            BodyComposition.query.filter_by(user_id=user_id)
            .order_by(BodyComposition.date.asc())
            .all()
        )
        return body_composition_objects

    def _convert_objects_to_object_lists(
        body_composition_objects: list,
    ) -> list[dict[str, str | float]]:
        body_composition_object_lists = [
            {
                "date": bco.date.strftime("%Y-%m-%d"),
                "weight": bco.weight,
                "body_fat": bco.body_fat,
            }
            for bco in body_composition_objects
        ]
        return body_composition_object_lists

    def _compute_monthly_averages_and_weight_change_rates(
        body_composition_df: DataFrame,
    ) -> DataFrame:
        monthly_averages_and_weight_change_rates_df = (
            body_composition_df.resample("ME").mean().round(2)
        )

        monthly_averages_and_weight_change_rates_df["weight_change_rate"] = (
            (
                monthly_averages_and_weight_change_rates_df["weight"]
                - monthly_averages_and_weight_change_rates_df["weight"].shift(
                    1
                )
            )
            / monthly_averages_and_weight_change_rates_df["weight"].shift(1)
            * 100
        ).round(2)

        monthly_averages_and_weight_change_rates_df.reset_index(inplace=True)
        monthly_averages_and_weight_change_rates_df["date"] = (
            monthly_averages_and_weight_change_rates_df["date"].dt.strftime(
                "%Y-%m"
            )
        )

        return monthly_averages_and_weight_change_rates_df

    def _convert_dataframe_to_json(df: DataFrame) -> list[dict[str, Any]]:
        json_data = df.to_json(orient="records")
        return json.loads(json_data)

    def _generate_dummy_data_object_list() -> list[dict[str, Any]]:
        duration = 365 * 3
        today = datetime.now()
        past_date = today - timedelta(days=int(duration))

        weight = round(random.uniform(90, 100), 2)
        body_fat = round(random.uniform(25, 30), 2)

        body_composition_object_lists = []
        while past_date <= today:
            weight_variation = round(random.uniform(-0.4, 0.36), 2)
            weight = round(max(weight + weight_variation, 50), 2)

            body_fat_variation = round(random.uniform(-0.2, 0.18), 2)
            body_fat = round(max(body_fat + body_fat_variation, 5), 2)

            body_composition_object = {
                "date": past_date.strftime("%Y-%m-%d"),
                "weight": weight,
                "body_fat": body_fat,
            }
            body_composition_object_lists.append(body_composition_object)

            past_date += timedelta(days=1)

        return body_composition_object_lists

    if current_user.is_authenticated:
        user_id = current_user.id
        body_composition_objects = _get_body_compositions(user_id)
        body_composition_object_lists = _convert_objects_to_object_lists(
            body_composition_objects
        )
    else:
        body_composition_object_lists = _generate_dummy_data_object_list()

    body_composition_df = pd.DataFrame(body_composition_object_lists)
    body_composition_df["date"] = pd.to_datetime(body_composition_df["date"])
    body_composition_df.set_index("date", inplace=True)
    monthly_averages_and_weight_change_rates_df = (
        _compute_monthly_averages_and_weight_change_rates(body_composition_df)
    )
    monthly_averages_and_weight_change_rates_json = _convert_dataframe_to_json(
        monthly_averages_and_weight_change_rates_df
    )

    return jsonify(
        body_composition_object_lists,
        monthly_averages_and_weight_change_rates_json,
    )
