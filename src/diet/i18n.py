# ruff: noqa: E501
from typing import Any

from flask import has_request_context, request, session, url_for

SUPPORTED_LANGUAGES = ("ja", "en")
DEFAULT_LANGUAGE = "ja"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "app.name": {"ja": "ダイエット", "en": "Diet"},
    "app.title": {"ja": "ダイエットアプリ", "en": "Diet App"},
    "meta.description": {
        "ja": "食事、体組成、健康目標を管理できるダイエットアプリです。",
        "en": "Track your diet, monitor body composition, and achieve your health goals with Diet App.",
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
    "form.username": {"ja": "ユーザー名", "en": "Username"},
    "form.email": {"ja": "メールアドレス", "en": "Email"},
    "form.password": {"ja": "パスワード", "en": "Password"},
    "form.confirm_password": {
        "ja": "パスワード確認",
        "en": "Confirm Password",
    },
    "form.current_password": {
        "ja": "現在のパスワード",
        "en": "Current Password",
    },
    "form.new_password": {"ja": "新しいパスワード", "en": "New Password"},
    "form.confirm_new_password": {
        "ja": "新しいパスワード確認",
        "en": "Confirm New Password",
    },
    "form.date": {"ja": "日付", "en": "Date"},
    "form.weight": {"ja": "体重", "en": "Weight"},
    "form.body_fat": {"ja": "体脂肪率", "en": "Body Fat Percentage"},
    "form.sign_up": {"ja": "サインアップ", "en": "Sign Up"},
    "form.sign_in": {"ja": "サインイン", "en": "Sign In"},
    "form.change_password": {
        "ja": "パスワードを変更",
        "en": "Change Password",
    },
    "form.update": {"ja": "更新", "en": "Update"},
    "form.submit": {"ja": "保存", "en": "Submit"},
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
    "auth.sign_up.title": {"ja": "サインアップ", "en": "Sign Up"},
    "auth.sign_in.title": {"ja": "サインイン", "en": "Sign In"},
    "auth.create_account": {
        "ja": "無料で新規アカウントを作成",
        "en": "Create a new account (free)",
    },
    "auth.already_member": {
        "ja": "すでに登録済みですか？",
        "en": "Already a member?",
    },
    "auth.account_menu.title": {
        "ja": "アカウントメニュー",
        "en": "Account Menu",
    },
    "auth.account_information.title": {
        "ja": "アカウント情報",
        "en": "Account Information",
    },
    "auth.change_email.title": {
        "ja": "メールアドレスを変更",
        "en": "Change Email",
    },
    "auth.change_password.title": {
        "ja": "パスワードを変更",
        "en": "Change Password",
    },
    "auth.deactivate_account.title": {
        "ja": "アカウントを無効化",
        "en": "Deactivate Account",
    },
    "auth.coming_soon": {
        "ja": "この機能は準備中です。",
        "en": "This feature is coming soon.",
    },
    "flash.signup_failed": {
        "ja": "サインアップに失敗しました。時間をおいて再度お試しください。",
        "en": "Sign-up failed. Please try again later.",
    },
    "flash.signed_up": {
        "ja": "サインアップしました。",
        "en": "Signed up successfully.",
    },
    "flash.signed_in": {
        "ja": "サインインしました。",
        "en": "Signed in successfully.",
    },
    "flash.signin_failed": {
        "ja": "サインインに失敗しました。メールアドレスまたはパスワードが正しくありません。",
        "en": "Sign-in failed. Invalid email or password.",
    },
    "flash.signed_out": {
        "ja": "サインアウトしました。",
        "en": "Signed out successfully.",
    },
    "flash.username_failed": {
        "ja": "ユーザー名の変更に失敗しました。時間をおいて再度お試しください。",
        "en": "Username change failed. Please try again later.",
    },
    "flash.username_changed": {
        "ja": "ユーザー名を変更しました。",
        "en": "Username changed successfully.",
    },
    "flash.password_failed": {
        "ja": "パスワードの変更に失敗しました。時間をおいて再度お試しください。",
        "en": "Password change failed. Please try again later.",
    },
    "flash.password_changed": {
        "ja": "パスワードを変更しました。",
        "en": "Password changed successfully.",
    },
    "flash.email_registered": {
        "ja": "このメールアドレスはすでに登録されています。",
        "en": "Email is already registered.",
    },
    "flash.invalid_current_password": {
        "ja": "現在のパスワードが正しくありません。",
        "en": "Invalid current password.",
    },
    "body_composition.record.title": {
        "ja": "体組成を記録",
        "en": "Record Body Composition",
    },
    "body_composition.record.heading": {
        "ja": "体組成を記録",
        "en": "Record Your Body Composition",
    },
    "dashboard.granularity": {"ja": "表示単位", "en": "Granularity"},
    "dashboard.duration": {"ja": "期間", "en": "Duration"},
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
    "nutrition.fat_per_100g": {
        "ja": "脂質 (g/100g)",
        "en": "Fat (g/100g)",
    },
    "nutrition.carbohydrates_per_100g": {
        "ja": "炭水化物 (g/100g)",
        "en": "Carbohydrates (g/100g)",
    },
    "nutrition.grams_per_unit": {
        "ja": "1単位あたりのグラム数 (g)",
        "en": "Grams Per Unit (g)",
    },
    "nutrition.minimum_intake": {
        "ja": "最小摂取量 (単位)",
        "en": "Minimum Intake (units)",
    },
    "nutrition.maximum_intake": {
        "ja": "最大摂取量 (単位)",
        "en": "Maximum Intake (units)",
    },
    "nutrition.actions": {"ja": "操作", "en": "Actions"},
    "nutrition.choose_food": {
        "ja": "食品データベースから選択",
        "en": "Choose from food database",
    },
    "nutrition.select_food": {"ja": "食品を選択", "en": "Select Food"},
    "nutrition.add_food": {"ja": "食品を追加", "en": "Add Food"},
    "nutrition.remove": {"ja": "削除", "en": "Remove"},
    "nutrition.select_food_from_database": {
        "ja": "食品データベースから選択",
        "en": "Select Food From Database",
    },
    "nutrition.close": {"ja": "閉じる", "en": "Close"},
    "nutrition.search": {"ja": "検索", "en": "Search"},
    "nutrition.search_food_placeholder": {
        "ja": "食品名または食品IDで検索",
        "en": "Search by name or food id",
    },
    "nutrition.sort_by": {"ja": "並び替え", "en": "Sort By"},
    "nutrition.name": {"ja": "名前", "en": "Name"},
    "nutrition.food_id": {"ja": "食品ID", "en": "Food ID"},
    "nutrition.order": {"ja": "順序", "en": "Order"},
    "nutrition.descending": {"ja": "降順", "en": "Descending"},
    "nutrition.ascending": {"ja": "昇順", "en": "Ascending"},
    "nutrition.food": {"ja": "食品", "en": "Food"},
    "nutrition.id": {"ja": "ID", "en": "ID"},
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
    "nutrition.add_constraint": {"ja": "制約を追加", "en": "Add Constraint"},
    "nutrition.optimize": {"ja": "最適化", "en": "Optimize"},
    "nutrition.results": {"ja": "結果", "en": "Results"},
    "js.other_nutrients": {"ja": "その他の栄養素", "en": "Other Nutrients"},
    "js.general": {"ja": "一般", "en": "General"},
    "js.select": {"ja": "選択", "en": "Select"},
    "js.daily": {"ja": "日次", "en": "Daily"},
    "js.monthly": {"ja": "月次", "en": "Monthly"},
    "js.7_days": {"ja": "7日", "en": "7 Days"},
    "js.30_days": {"ja": "30日", "en": "30 Days"},
    "js.90_days": {"ja": "90日", "en": "90 Days"},
    "js.180_days": {"ja": "180日", "en": "180 Days"},
    "js.6_months": {"ja": "6か月", "en": "6 Months"},
    "js.1_year": {"ja": "1年", "en": "1 Year"},
    "js.3_years": {"ja": "3年", "en": "3 Years"},
    "js.date": {"ja": "日付", "en": "Date"},
    "js.no_data": {"ja": "データがありません。", "en": "No data available."},
    "js.csrf_missing": {
        "ja": "CSRFトークンがありません。",
        "en": "CSRF token is missing",
    },
    "js.weight": {"ja": "体重", "en": "Weight"},
    "js.body_fat_percentage": {"ja": "体脂肪率", "en": "Body Fat Percentage"},
    "js.weight_kg": {"ja": "体重 (kg)", "en": "Weight (kg)"},
    "js.body_fat_percentage_percent": {
        "ja": "体脂肪率 (%)",
        "en": "Body Fat Percentage (%)",
    },
    "js.average_weight": {"ja": "平均体重", "en": "Average Weight"},
    "js.average_body_fat_percentage": {
        "ja": "平均体脂肪率",
        "en": "Average Body Fat Percentage",
    },
    "js.average_weight_kg": {
        "ja": "平均体重 (kg)",
        "en": "Average Weight (kg)",
    },
    "js.average_body_fat_percentage_percent": {
        "ja": "平均体脂肪率 (%)",
        "en": "Average Body Fat Percentage (%)",
    },
    "js.change_rate_last_month": {
        "ja": "前月比 (%)",
        "en": "Change Rate from Last Month (%)",
    },
    "js.trends_title": {
        "ja": "体重と体脂肪率の推移",
        "en": "Trends in Weight and Body Fat Percentage",
    },
    "js.chart_unavailable": {
        "ja": "Chart.jsを利用できません。",
        "en": "Chart.js is unavailable.",
    },
    "js.protein": {"ja": "たんぱく質", "en": "Protein"},
    "js.fat": {"ja": "脂質", "en": "Fat"},
    "js.carbohydrates": {"ja": "炭水化物", "en": "Carbohydrates"},
    "js.pfc_ratio": {"ja": "PFCバランス", "en": "PFC Ratio"},
    "js.total_energy": {"ja": "総エネルギー", "en": "Total Energy"},
    "js.percentage": {"ja": "割合", "en": "Percentage"},
    "js.food_intakes": {"ja": "食品摂取量", "en": "Food Intakes"},
    "js.food_item": {"ja": "食品", "en": "Food Item"},
    "js.units": {"ja": "単位", "en": "Units"},
    "js.status": {"ja": "ステータス", "en": "status"},
    "js.message": {"ja": "メッセージ", "en": "message"},
}


def get_locale() -> str:
    if not has_request_context():
        return DEFAULT_LANGUAGE

    query_language = request.args.get("lang")
    if query_language in SUPPORTED_LANGUAGES:
        session["lang"] = query_language
        return query_language

    session_language = session.get("lang")
    if session_language in SUPPORTED_LANGUAGES:
        return session_language

    browser_language = request.accept_languages.best_match(SUPPORTED_LANGUAGES)
    return browser_language or DEFAULT_LANGUAGE


def translate(key: str) -> str:
    translations = TRANSLATIONS.get(key, {})
    return (
        translations.get(get_locale())
        or translations.get(DEFAULT_LANGUAGE)
        or key
    )


def localized_url(language: str) -> str:
    view_args: dict[str, Any] = (
        request.view_args.copy() if request.view_args else {}
    )
    query_args: dict[str, Any] = request.args.to_dict(flat=True)
    query_args["lang"] = language

    values = {**view_args, **query_args}

    return url_for(request.endpoint or "main.index", **values)


def javascript_translations() -> dict[str, str]:
    return {
        key: translate(key) for key in TRANSLATIONS if key.startswith("js.")
    }
