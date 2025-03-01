import json

from pandas import DataFrame

from apps.body_composition.models import BodyComposition


class BodyCompositionUtil:
    @staticmethod
    def df_to_json(df: DataFrame) -> list[dict[str, float]]:
        str_json = df.to_json(orient="records")
        json_data = json.loads(str_json)
        return json_data

    @staticmethod
    def body_compositions_to_dicts(
        body_compositions: list[BodyComposition],
    ) -> list[dict[str, str | float]]:
        return [
            {
                "date": body_composition.date.strftime("%Y-%m-%d"),
                "weight": body_composition.weight,
                "body_fat": body_composition.body_fat,
            }
            for body_composition in body_compositions
        ]
