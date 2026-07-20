# ruff: noqa: E501

COMMON_TRANSLATIONS: dict[str, dict[str, str]] = {
    "app.name": {"ja": "ダイエット", "en": "Diet"},
    "app.title": {"ja": "ダイエットアプリ", "en": "Diet App"},
    "meta.description": {
        "ja": "食事、体組成、健康目標を管理できるダイエットアプリです。",
        "en": "Track your diet, monitor body composition, and "
        "achieve your health goals with Diet App.",
    },
    "meta.keywords": {
        "ja": "ダイエット 健康 トレーニング フィットネス",
        "en": "Diet Health Training Fitness",
    },
    "language.japanese": {"ja": "日本語", "en": "日本語"},
    "language.english": {"ja": "English", "en": "English"},
    "nav.home": {"ja": "ホーム", "en": "Home"},
    "nav.nutrition_optimizer": {
        "ja": "栄養最適化",
        "en": "Nutrition Optimizer",
    },
    "nav.record_body_composition": {
        "ja": "体組成を記録",
        "en": "Record Body Composition",
    },
    "nav.account": {"ja": "アカウント", "en": "Account"},
    "nav.sign_out": {"ja": "サインアウト", "en": "Sign Out"},
    "nav.sign_up": {"ja": "サインアップ", "en": "Sign Up"},
    "nav.sign_in": {"ja": "サインイン", "en": "Sign In"},
    "nav.language": {"ja": "Language", "en": "言語"},
    "theme.light": {"ja": "ライト", "en": "Light"},
    "theme.dark": {"ja": "ダーク", "en": "Dark"},
    "theme.auto": {"ja": "自動", "en": "Auto"},
    "error.404.title": {"ja": "404 見つかりません", "en": "404 Not Found"},
    "error.500.title": {
        "ja": "500 サーバーエラー",
        "en": "500 Internal Server Error",
    },
    "validation.required": {
        "ja": "この項目は必須です。",
        "en": "This field is required.",
    },
    "validation.email": {
        "ja": "有効なメールアドレスを入力してください。",
        "en": "Invalid email address.",
    },
    "validation.equal_to": {
        "ja": "%(other_label)sと一致している必要があります。",
        "en": "Field must be equal to %(other_name)s.",
    },
    "validation.length_between": {
        "ja": "%(min)d文字以上%(max)d文字以下で入力してください。",
        "en": "Field must be between %(min)d and %(max)d characters long.",
    },
    "validation.number_range": {
        "ja": "%(min)s以上%(max)s以下で入力してください。",
        "en": "Number must be between %(min)s and %(max)s.",
    },
}
