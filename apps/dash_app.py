from datetime import datetime

import dash
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output

weight_data = [100, 95, 90, 85, 80, 75, 70, 65, 120, 110]
body_fat_data = [23, 22, 22.5, 21.5, 22, 21, 21.5, 20.5, 21, 23]
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


dates = [datetime.strptime(date, "%Y-%m-%d").date() for date in dates]


def init_dash(app):
    # Dashアプリケーションのレイアウトを定義
    app.layout = html.Div([dcc.Graph(id="combined-graph")])

    # 体重と体脂肪率のグラフを作成するコールバック関数
    @app.callback(Output("combined-graph", "figure"), [Input("combined-graph", "id")])
    def update_combined_graph(input_id):
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
