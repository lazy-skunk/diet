import random
from datetime import datetime, timedelta


class SampleBodyCompositionService:
    @staticmethod
    def generate_sample_data(
        duration_days: int = 365 * 3,
    ) -> list[dict[str, str | float]]:
        today = datetime.now()
        past_date = today - timedelta(days=duration_days)
        date_pointer = past_date

        weight = round(random.uniform(90, 100), 2)
        body_fat = round(random.uniform(25, 30), 2)

        sample_data: list[dict[str, str | float]] = []
        while date_pointer <= today:
            weight_variation = round(random.uniform(-0.4, 0.36), 2)
            weight = round(max(weight + weight_variation, 50), 2)

            body_fat_variation = round(random.uniform(-0.2, 0.18), 2)
            body_fat = round(max(body_fat + body_fat_variation, 5), 2)

            sample_data.append(
                {
                    "date": date_pointer.strftime("%Y-%m-%d"),
                    "weight": weight,
                    "body_fat": body_fat,
                }
            )

            date_pointer += timedelta(days=1)

        return sample_data
