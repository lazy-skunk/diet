from diet.body_composition.service import compute_monthly_statistics


def test_compute_monthly_statistics_returns_empty_for_no_data() -> None:
    assert compute_monthly_statistics([]) == []


def test_compute_monthly_statistics_calculates_monthly_average() -> None:
    result = compute_monthly_statistics(
        [
            {"date": "2026-05-01", "weight": 70.0, "body_fat": 20.0},
            {"date": "2026-05-31", "weight": 72.0, "body_fat": 18.0},
        ]
    )

    assert result == [
        {
            "date": "2026-05",
            "weight": 71.0,
            "body_fat": 19.0,
            "weight_change_rate": None,
        }
    ]


def test_compute_monthly_statistics_calculates_weight_change_rate() -> None:
    result = compute_monthly_statistics(
        [
            {"date": "2026-05-01", "weight": 100.0, "body_fat": 20.0},
            {"date": "2026-06-01", "weight": 110.0, "body_fat": 19.0},
        ]
    )

    assert result == [
        {
            "date": "2026-05",
            "weight": 100.0,
            "body_fat": 20.0,
            "weight_change_rate": None,
        },
        {
            "date": "2026-06",
            "weight": 110.0,
            "body_fat": 19.0,
            "weight_change_rate": 10.0,
        },
    ]
