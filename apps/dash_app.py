import random
from datetime import datetime, timedelta

import dash
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html
from flask import g

from .models import BodyComposition


def init_dash(app):
    app.layout = html.Div(
        [
            html.Label("表示期間", id="duration-label"),
            dcc.Dropdown(
                id="duration-dropdown",
                options=[
                    {"label": "1週間", "value": "7"},
                    {"label": "1か月", "value": "30"},
                    {"label": "3か月", "value": "90"},
                    {"label": "半年", "value": "180"},
                    {"label": "1年", "value": "365"},
                    {"label": "全期間", "value": "all"},
                ],
                value="7",
                clearable=False,
            ),
            dcc.Graph(id="body_composition_graph"),
        ]
    )

    @app.callback(
        Output("body_composition_graph", "figure"),
        [Input("duration-dropdown", "value")],
    )
    def update_graph_by_duration(duration):
        user_id = g.user.id if g.user.is_authenticated else None
        weight_data, body_fat_data, dates = get_body_composition_data(user_id, duration)

        trace1 = go.Scatter(
            x=dates,
            y=weight_data,
            mode="lines+markers",
            name="体重",
            yaxis="y1",
            marker=dict(symbol="circle"),
        )

        trace2 = go.Scatter(
            x=dates,
            y=body_fat_data,
            mode="lines+markers",
            name="体脂肪率",
            yaxis="y2",
            marker=dict(symbol="circle"),
        )

        layout = go.Layout(
            title="体重と体脂肪率の推移",
            xaxis=dict(title="日付"),
            yaxis=dict(title="体重（kg）", side="left", showgrid=False),
            yaxis2=dict(title="体脂肪率（%）", side="right", overlaying="y", showgrid=False),
            legend=dict(x=0.01, y=0.98),
        )

        return {"data": [trace1, trace2], "layout": layout}


def get_body_composition_data(user_id, duration=None):
    weight_data = []
    body_fat_data = []
    dates = []

    if user_id is None:
        weight_data, body_fat_data, dates = generate_dummy_data(duration)
        return weight_data, body_fat_data, dates

    if user_id is not None and duration.isnumeric():
        today = datetime.now()
        start_date = today - timedelta(days=int(duration))
        body_compositions = (
            BodyComposition.query.filter_by(user_id=user_id)
            .filter(BodyComposition.date >= start_date)
            .all()
        )
    else:
        body_compositions = BodyComposition.query.filter_by(user_id=user_id).all()

    print(body_compositions)
    for body_composition in body_compositions:
        weight_data.append(body_composition.weight)
        body_fat_data.append(body_composition.body_fat)
        dates.append(body_composition.date)

    return weight_data, body_fat_data, dates


def generate_dummy_data(duration):
    weight_data = []
    body_fat_data = []
    dates = []
    today = datetime.now()

    if duration == "all":
        duration = 365 * 1.5

    dummy_date = today - timedelta(days=int(duration))

    prev_weight = round(random.uniform(80, 100), 1)
    prev_body_fat = round(random.uniform(25, 40), 1)

    while dummy_date <= today:
        weight_variation = round(random.uniform(-0.4, 0.35), 1)
        weight = max(prev_weight + weight_variation, 50)
        weight_data.append(weight + weight_variation)

        body_fat_variation = round(random.uniform(-0.2, 0.15), 1)
        body_fat = max(prev_body_fat + body_fat_variation, 5)
        body_fat_data.append(body_fat)

        dates.append(dummy_date.strftime("%Y-%m-%d"))

        dummy_date += timedelta(days=1)
        prev_weight = weight
        prev_body_fat = body_fat

    return weight_data, body_fat_data, dates
