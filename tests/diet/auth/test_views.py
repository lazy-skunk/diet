from flask.testing import FlaskClient


def test_signin_page(client: FlaskClient) -> None:
    response = client.get("/auth/signin")
    assert response.status_code == 200

    # 正しいアカウント情報でサインインした場合、
    # ホームページに遷移することの確認をする。
    # 誤ったアカウント情報でサインインした場合、
    # エラーメッセージが表示されることを確認する。


def test_signup_page(client: FlaskClient) -> None:
    response = client.get("/auth/signup")
    assert response.status_code == 200

    # 既存のユーザー名でサインアップをした場合、エラーになることを確認する。
    # 既存のメールアドレスでサインアップした場合、エラーになることを確認する。
    # パスワードとパスワード（確認用）の値が異なる場合はエラーを表示する。
    # 体重に文字列を入力した場合にエラーが表示されること。
    # 体脂肪率に文字列を入れた場合にエラーが表示されること。
    # 体脂肪率は入力せずとも登録できること。


class TestSignout:
    # ログアウトが成功し、ホームページに遷移することの確認をする。
    # ログインしていない場合はログインページに遷移すること。
    pass
