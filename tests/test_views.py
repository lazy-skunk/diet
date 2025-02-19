import unittest

from apps.app import create_app


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()


class IndexPageTest(BaseTestCase):
    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class LogBodyCompositionTest(BaseTestCase):
    # 未ログインの場合は、ログインページに遷移すること。
    # ログイン済みの場合は体重記録のページに遷移すること。
    # ログイン済みの場合は入力欄の初期値が最新の情報になっていること。（日付は今日になっていればよかったはず。）
    # 正しい値を入力した場合、登録されてホームページに遷移すること。
    # 不正な値を入力した場合、エラーが表示されること。
    # 登録済みの値を更新できること。
    pass


class SigninPageTest(BaseTestCase):
    def test_signin_page(self):
        response = self.client.get("/signin")
        self.assertEqual(response.status_code, 200)

    # 正しいアカウント情報でサインインした場合、ホームページに遷移することの確認をする。
    # 誤ったアカウント情報でサインインした場合、エラーメッセージが表示されることを確認する。


class SignupPageTest(BaseTestCase):
    def test_signup_page(self):
        response = self.client.get("/signup")
        self.assertEqual(response.status_code, 200)

    # 既存のユーザー名でサインアップをした場合、エラーになることを確認する。
    # 既存のメールアドレスでサインアップした場合、エラーになることを確認する。
    # パスワードとパスワード（確認用）の値が異なっている場合はエラーを表示すること。
    # 体重に文字列を入力した場合にエラーが表示されること。
    # 体脂肪率に文字列を入れた場合にエラーが表示されること。
    # 体脂肪率は入力せずとも登録できること。


class LogoutTest(BaseTestCase):
    # ログアウトが成功し、ホームページに遷移することの確認をする。
    # ログインしていない場合はログインページに遷移すること。
    pass


class FetchBodyCompositionDataTest(BaseTestCase):
    # 未ログインの場合はサンプルデータが返ってきていること。
    # ログインしている場合は、そのユーザーの情報が返ってきていること。
    pass


if __name__ == "__main__":
    unittest.main()
