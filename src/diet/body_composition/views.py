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
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response

from diet.body_composition.api_models import (
    create_body_composition_data_response,
)
from diet.body_composition.sample_data import generate_sample_data
from diet.body_composition.service import (
    compute_monthly_statistics,
    get_body_composition_dicts,
    init_form_data,
    upsert_body_composition,
)

from .forms import RecordBodyCompositionForm

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
        form_data = init_form_data(user_id)
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
            upsert_body_composition(user_id, input_date, weight, body_fat)
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


@blueprint.route("/get_body_composition_data", methods=["GET"])
def get_body_composition_data() -> Response:
    if current_user.is_authenticated:
        user_id = current_user.id
        body_composition_data = get_body_composition_dicts(user_id)
    else:
        body_composition_data = generate_sample_data()

    monthly_statistics = compute_monthly_statistics(body_composition_data)

    response = create_body_composition_data_response(
        body_composition_data, monthly_statistics
    )
    return jsonify(response.model_dump(by_alias=True))
