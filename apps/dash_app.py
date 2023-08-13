import random
from datetime import datetime, timedelta

import dash
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html
from flask import g

from .models import BodyComposition


def init_dash(app):
    """
    Dashアプリケーションの初期設定を行う関数。

    Parameters:
    - app (dash.Dash): 初期化するDashアプリケーションのインスタンス。

    Details:
    この関数は以下のステップでDashアプリケーションの初期設定を行います。
    1. レイアウトの定義: 期間のドロップダウンメニューと、体組成のグラフを表示するDiv領域を設定します。
    2. コールバックの定義:
        - 期間ドロップダウンの値が変更されたときに、グラフを更新するコールバック。
        - グラフのデータが空の場合に、「表示するデータがありません。体重を記録してください。」というメッセージを表示するコールバック。
    """
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
            html.Div(
                id="graph-overlay-container",
                children=[
                    dcc.Graph(id="body_composition_graph"),
                    html.Div(id="no-data-message"),
                ],
            ),
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

    @app.callback(
        Output("no-data-message", "children"),
        Output("no-data-message", "style"),
        [Input("body_composition_graph", "figure")],
    )
    def display_no_data_message(figure):
        if not figure["data"] or len(figure["data"][0]["y"]) == 0:
            return "表示するデータがありません。体重を記録してください。", {"display": "block"}
        else:
            return None, {"display": "none"}


def get_body_composition_data(user_id, duration=None):
    """
    指定されたユーザーIDと期間に対応する体組成情報を取得する関数。

    Parameters:
    - user_id (int or None): ユーザーのID。未ログイン時はNone。
    - duration (str or None): データを取得する期間(日数)。Noneの場合、全期間のデータを取得。

    Returns:
    - tuple: 3つのリストを返す。
        1. weight_data (list of float): 体重のデータ。
        2. body_fat_data (list of float): 体脂肪率のデータ。
        3. dates (list of str): データの日付のリスト（"%Y-%m-%d"形式）。

    Notes:
    - user_idがNoneの場合(未ログイン時)、ダミーデータが返される。
    - durationが指定されていれば、その期間のデータを取得。指定されていなければ、ユーザーの全期間のデータを取得。
    - データは日付の昇順で取得する。
    """
    weight_data = []
    body_fat_data = []
    dates = []

    # 未ログイン時はダミーデータを表示する。
    if user_id is None:
        weight_data, body_fat_data, dates = generate_dummy_data(duration)
        return weight_data, body_fat_data, dates

    # 表示期間に応じたデータを表示する。
    if user_id is not None and duration.isnumeric():
        today = datetime.now()
        start_date = today - timedelta(days=int(duration))

        body_compositions = (
            BodyComposition.query.filter_by(user_id=user_id)
            .filter(BodyComposition.date >= start_date)
            .order_by(BodyComposition.date.asc())
            .all()
        )
    else:
        body_compositions = (
            BodyComposition.query.filter_by(user_id=user_id)
            .order_by(BodyComposition.date.asc())
            .all()
        )

    # 取得したデータを各情報ごとの配列に格納する。
    for body_composition in body_compositions:
        weight_data.append(body_composition.weight)
        body_fat_data.append(body_composition.body_fat)
        dates.append(body_composition.date)

    return weight_data, body_fat_data, dates


def generate_dummy_data(duration):
    """
    ユーザーの体重と体脂肪率のダミーデータを生成する関数。

    Parameters:
    - duration (str or int): ダミーデータを生成する期間。"all" または 日数の整数値。

    Returns:
    - list: 3つのリストを返す。
        1. weight_data (list of float): 体重のダミーデータ。
        2. body_fat_data (list of float): 体脂肪率のダミーデータ。
        3. dates (list of str): データの日付のリスト（"%Y-%m-%d"形式）。

    Notes:
    - duration が "all" の場合、デフォルトで2年分のダミーデータを生成する。
    - 初期体重と体脂肪率はランダムに設定される。
    - 体重と体脂肪率の変動はランダムに計算されるが、一定の範囲内で変動する。
    - 体重は50kg未満にならないように制限されている。
    - 体脂肪率は5%未満にならないように制限されている。
    """
    # ダミーデータに全期間の概念は無いので、とりあえず2年分のデータを生成します。
    if duration == "all":
        duration = 365 * 2

    today = datetime.now()
    dummy_date = today - timedelta(days=int(duration))

    initial_weight = round(random.uniform(80, 100), 1)
    initial_body_fat = round(random.uniform(25, 30), 1)

    current_weight = initial_weight
    current_body_fat = initial_body_fat

    dates = []
    weight_data = []
    body_fat_data = []
    while dummy_date <= today:
        dates.append(dummy_date.strftime("%Y-%m-%d"))
        dummy_date += timedelta(days=1)

        weight_variation = round(random.uniform(-0.3, 0.27), 2)
        updated_weight = max(current_weight + weight_variation, 50)
        weight_data.append(updated_weight)
        current_weight = updated_weight

        body_fat_variation = round(random.uniform(-0.2, 0.18), 2)
        updated_body_fat = max(current_body_fat + body_fat_variation, 5)
        body_fat_data.append(updated_body_fat)
        current_body_fat = updated_body_fat

    return weight_data, body_fat_data, dates
