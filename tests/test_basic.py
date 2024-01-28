import unittest
from apps.app import create_app

class BasicTests(unittest.TestCase):
    def setUp(self):
        # テスト用のアプリインスタンスを作成
        self.app = create_app('testing')
        self.client = self.app.test_client()

        # アプリコンテキストをプッシュ
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # アプリコンテキストをポップ
        self.app_context.pop()

    def test_home_page(self):
        # ホームページにアクセス
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('サンプルデータを表示しています。', response.data.decode())

if __name__ == '__main__':
    unittest.main()
