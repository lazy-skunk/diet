from datetime import datetime

import dash
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import g

from .models import BodyComposition


def init_dash(app):
    app.layout = html.Div([dcc.Graph(id="combined-graph")])

    @app.callback(Output("combined-graph", "figure"), [Input("combined-graph", "id")])
    def update_combined_graph(input_id):
        user_id = g.user.id if g.user.is_authenticated else None
        weight_data, body_fat_data, dates = get_data_from_db(user_id)

        trace1 = go.Scatter(
            x=dates,
            y=weight_data,
            mode="lines+markers",
            name="体重",
            yaxis="y1",
            marker=dict(symbol="star"),
        )

        trace2 = go.Scatter(
            x=dates,
            y=body_fat_data,
            mode="lines+markers",
            name="体脂肪率",
            yaxis="y2",
            marker=dict(symbol="diamond"),
        )

        layout = go.Layout(
            title="体重と体脂肪率の推移",
            xaxis=dict(title="日付"),
            yaxis=dict(title="体重（kg）", side="left", showgrid=False),
            yaxis2=dict(title="体脂肪率（%）", side="right", overlaying="y", showgrid=False),
            legend=dict(x=0.01, y=0.98),
        )

        return {"data": [trace1, trace2], "layout": layout}


def get_data_from_db(user_id):
    if user_id is None:
        weight_data = [100, 95, 96, 91, 92, 87, 88, 83, 84, 79]
        body_fat_data = [23, 22, 21, 20, 19, 18, 17, 16, 15, 14]
        dates = [
            "2023-08-01",
            "2023-08-02",
            "2023-08-03",
            "2023-08-04",
            "2023-08-05",
            "2023-08-06",
            "2023-08-07",
            "2023-08-08",
            "2023-08-09",
            "2023-08-10",
        ]
    else:
        weight_data = []
        body_fat_data = []
        dates = []
        body_compositions = BodyComposition.query.filter_by(user_id=user_id).all()
        for body_composition in body_compositions:
            weight_data.append(body_composition.weight)
            body_fat_data.append(body_composition.body_fat)
            dates.append(body_composition.date)

    return weight_data, body_fat_data, dates
