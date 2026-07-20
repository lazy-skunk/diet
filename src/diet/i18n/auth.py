# ruff: noqa: E501

AUTH_TRANSLATIONS: dict[str, dict[str, str]] = {
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
    "form.sign_up": {"ja": "サインアップ", "en": "Sign Up"},
    "form.sign_in": {"ja": "サインイン", "en": "Sign In"},
    "form.change_password": {
        "ja": "パスワードを変更",
        "en": "Change Password",
    },
    "form.update": {"ja": "更新", "en": "Update"},
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
}
