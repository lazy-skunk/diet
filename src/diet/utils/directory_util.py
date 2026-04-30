import os


class DirectoryUtil:
    @staticmethod
    def ensure_directory(path: str) -> None:
        dir_path = path if os.path.isdir(path) else os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
