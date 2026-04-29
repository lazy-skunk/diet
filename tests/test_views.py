import pytest

from apps.app import create_app


@pytest.fixture
def app():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    yield app
    app_context.pop()


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


class TestLogBodyComposition:
    # 未ログインの場合は、ログインページに遷移すること。
    # ログイン済みの場合は体重記録のページに遷移すること。
    # ログイン済みの場合は入力欄の初期値が最新の情報になっていること。
    # （日付は今日になっていればよかったはず。）
    # 正しい値を入力した場合、登録されてホームページに遷移すること。
    # 不正な値を入力した場合、エラーが表示されること。
    # 登録済みの値を更新できること。
    pass


def test_signin_page(client):
    response = client.get("/auth/signin")
    assert response.status_code == 200

    # 正しいアカウント情報でサインインした場合、
    # ホームページに遷移することの確認をする。
    # 誤ったアカウント情報でサインインした場合、
    # エラーメッセージが表示されることを確認する。


def test_signup_page(client):
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


class TestFetchBodyCompositionData:
    # 未ログインの場合はサンプルデータが返ってきていること。
    # ログインしている場合は、そのユーザーの情報が返ってきていること。
    pass
