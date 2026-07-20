# ruff: noqa: E501

NUTRITION_OPTIMIZER_TRANSLATIONS: dict[str, dict[str, str]] = {
    "nutrition.title": {"ja": "栄養最適化", "en": "Nutrition Optimizer"},
    "nutrition.food_information": {"ja": "食品情報", "en": "Food Information"},
    "nutrition.filter_nutrients": {
        "ja": "栄養素を絞り込み",
        "en": "Filter Nutrients",
    },
    "nutrition.search_nutrient_placeholder": {
        "ja": "栄養素名、カテゴリ、識別子で検索",
        "en": "Search nutrient name, category, or identifier",
    },
    "nutrition.food_name": {"ja": "食品名", "en": "Food Name"},
    "nutrition.energy_per_100g": {
        "ja": "エネルギー (kcal/100g)",
        "en": "Energy (kcal/100g)",
    },
    "nutrition.protein_per_100g": {
        "ja": "たんぱく質 (g/100g)",
        "en": "Protein (g/100g)",
    },
    "nutrition.fat_per_100g": {"ja": "脂質 (g/100g)", "en": "Fat (g/100g)"},
    "nutrition.carbohydrates_per_100g": {
        "ja": "炭水化物 (g/100g)",
        "en": "Carbohydrates (g/100g)",
    },
    "nutrition.minimum_intake_grams": {
        "ja": "最小摂取量 (g)",
        "en": "Minimum Intake (g)",
    },
    "nutrition.maximum_intake_grams": {
        "ja": "最大摂取量 (g)",
        "en": "Maximum Intake (g)",
    },
    "nutrition.actions": {"ja": "操作", "en": "Actions"},
    "nutrition.choose_food": {
        "ja": "食品名を入力、または食品一覧から選択",
        "en": "Enter a food name or choose from food catalog",
    },
    "nutrition.select_food": {
        "ja": "食品一覧から選択",
        "en": "Select from food catalog",
    },
    "nutrition.select_food_from_catalog": {
        "ja": "食品一覧から選択",
        "en": "Select Food From Catalog",
    },
    "nutrition.search": {"ja": "検索", "en": "Search"},
    "nutrition.search_food_placeholder": {
        "ja": "食品名で検索",
        "en": "Search by name",
    },
    "nutrition.loading_foods": {
        "ja": "食品一覧を読み込んでいます…",
        "en": "Loading food catalog…",
    },
    "nutrition.sort_by": {"ja": "並び替え", "en": "Sort By"},
    "nutrition.name": {"ja": "名前", "en": "Name"},
    "nutrition.order": {"ja": "順序", "en": "Order"},
    "nutrition.descending": {"ja": "降順", "en": "Descending"},
    "nutrition.ascending": {"ja": "昇順", "en": "Ascending"},
    "nutrition.previous": {"ja": "前へ", "en": "Previous"},
    "nutrition.next": {"ja": "次へ", "en": "Next"},
    "nutrition.food": {"ja": "食品", "en": "Food"},
    "nutrition.action": {"ja": "操作", "en": "Action"},
    "nutrition.objective": {"ja": "目的関数", "en": "Objective"},
    "nutrition.sense": {"ja": "方向", "en": "Sense"},
    "nutrition.nutrient": {"ja": "栄養素", "en": "Nutrient"},
    "nutrition.minimize": {"ja": "最小化", "en": "Minimize"},
    "nutrition.maximize": {"ja": "最大化", "en": "Maximize"},
    "nutrition.energy": {"ja": "エネルギー", "en": "Energy"},
    "nutrition.protein": {"ja": "たんぱく質", "en": "Protein"},
    "nutrition.fat": {"ja": "脂質", "en": "Fat"},
    "nutrition.carbohydrates": {"ja": "炭水化物", "en": "Carbohydrates"},
    "nutrition.constraints": {"ja": "制約条件", "en": "Constraints"},
    "nutrition.min_max": {"ja": "最小/最大", "en": "Min/Max"},
    "nutrition.unit": {"ja": "単位", "en": "Unit"},
    "nutrition.value": {"ja": "値", "en": "Value"},
    "nutrition.minimum": {"ja": "最小", "en": "Minimum"},
    "nutrition.maximum": {"ja": "最大", "en": "Maximum"},
    "nutrition.optimize": {"ja": "最適化", "en": "Optimize"},
    "nutrition.results": {"ja": "結果", "en": "Results"},
    "js.other_nutrients": {"ja": "その他の栄養素", "en": "Other Nutrients"},
    "js.general": {"ja": "一般", "en": "General"},
    "js.select": {"ja": "選択", "en": "Select"},
    "js.food_result_count": {"ja": "{count}件", "en": "{count} items"},
    "js.food_page_status": {
        "ja": "{current} / {total}ページ",
        "en": "Page {current} of {total}",
    },
    "js.no_matching_foods": {
        "ja": "該当する食品がありません。",
        "en": "No matching foods were found.",
    },
    "js.food_name_required": {
        "ja": "食品名を入力してください。",
        "en": "Please enter a food name.",
    },
    "js.duplicate_food_name": {
        "ja": "同じ食品名を複数追加できません。",
        "en": "The same food name cannot be added more than once.",
    },
    "js.invalid_intake_grams_range": {
        "ja": "最大摂取量は最小摂取量以上にしてください。",
        "en": "Maximum intake must be greater than "
        "or equal to minimum intake.",
    },
    "js.protein": {"ja": "たんぱく質", "en": "Protein"},
    "js.fat": {"ja": "脂質", "en": "Fat"},
    "js.carbohydrates": {"ja": "炭水化物", "en": "Carbohydrates"},
    "js.pfc_composition_ratio": {
        "ja": "PFCバランス（PFC内構成比率）",
        "en": "PFC Balance (PFC Composition Ratio)",
    },
    "js.total_energy": {"ja": "総エネルギー", "en": "Total Energy"},
    "js.percentage": {"ja": "割合", "en": "Percentage"},
    "js.food_intake": {"ja": "食品摂取量", "en": "Food Intake"},
    "js.food_item": {"ja": "食品", "en": "Food Item"},
    "js.intake_grams": {"ja": "摂取量 (g)", "en": "Intake (g)"},
    "js.status": {"ja": "ステータス", "en": "status"},
    "js.message": {"ja": "メッセージ", "en": "message"},
    "js.unexpected_response": {
        "ja": "処理中に問題が発生しました。しばらくしてからもう一度お試しください。",
        "en": "A problem occurred. Please wait a moment and try again.",
    },
    "js.invalid_input": {
        "ja": "入力内容に問題があります。内容を確認して、もう一度お試しください。",
        "en": "There is a problem with the input. Please review "
        "it and try again.",
    },
    "js.request_verification_failed": {
        "ja": "リクエストを送信できませんでした。ページを再読み込みして、もう一度お試しください。",
        "en": "The request could not be "
        "submitted. Please reload the page "
        "and try again.",
    },
    "js.optimization_infeasible": {
        "ja": "条件を満たす組み合わせが見つかりませんでした。制約条件と食品の摂取量範囲を見直してください。",
        "en": "No combination satisfying the "
        "conditions was found. Please review "
        "the constraints and food intake "
        "ranges.",
    },
    "js.optimization_failed": {
        "ja": "計算を完了できませんでした。条件を見直して、もう一度お試しください。",
        "en": "The calculation could not be completed. "
        "Please review the conditions and try "
        "again.",
    },
}
