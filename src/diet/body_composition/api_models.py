from pydantic import BaseModel, ConfigDict


def _to_camel(snake_case_str: str) -> str:
    words = snake_case_str.split("_")
    return "".join(
        word.capitalize() if index != 0 else word
        for index, word in enumerate(words)
    )


class BodyCompositionApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        loc_by_alias=False,
        extra="forbid",
    )


class BodyCompositionData(BodyCompositionApiModel):
    date: str
    weight: float
    body_fat: float | None


class MonthlyStatistics(BodyCompositionApiModel):
    date: str
    weight: float | None
    body_fat: float | None
    weight_change_rate: float | None


class BodyCompositionDataResponse(BodyCompositionApiModel):
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
