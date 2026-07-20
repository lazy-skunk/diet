from diet.api_models import ApiModel


class BodyCompositionData(ApiModel):
    date: str
    weight: float
    body_fat: float | None


class MonthlyStatistics(ApiModel):
    date: str
    weight: float | None
    body_fat: float | None
    weight_change_rate: float | None


class BodyCompositionDataResponse(ApiModel):
    body_compositions: list[BodyCompositionData]
    monthly_statistics: list[MonthlyStatistics]


def create_body_composition_data_response(
    body_compositions: list[BodyCompositionData],
    monthly_statistics: list[MonthlyStatistics],
) -> BodyCompositionDataResponse:
    return BodyCompositionDataResponse(
        body_compositions=body_compositions,
        monthly_statistics=monthly_statistics,
    )
