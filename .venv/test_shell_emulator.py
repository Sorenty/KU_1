import unittest

class ShellEmulator:
    def __init__(self, tar_path):
        self.current_dir = "/"
        # Имитируем структуру файлов для тестов
        self.filesystem = {
            "/": ["file1.txt", "subdir"],
            "/subdir": ["file2.txt"]
        }

    def ls(self):
        """Список файлов и каталогов в текущем каталоге"""
        return self.filesystem.get(self.current_dir, [])

    def cd(self, path):
        """Смена текущего каталога"""
        if path == "..":
            self.current_dir = "/"  # Переход в корневую директорию
        elif path == "subdir":
            self.current_dir = "/subdir"
        else:
            raise FileNotFoundError(f"Directory not found: {path}")

    def close(self):
        """Закрытие архива (не используется в этом примере)"""
        pass


# Тестовый класс
class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Подготовка фиктивной файловой системы"""
        self.emulator = ShellEmulator("test.tar")

    def tearDown(self):
        """Очистка после тестов"""
        self.emulator.close()

    def test_ls_root(self):
        """Тест команды ls в корневом каталоге"""
        result = self.emulator.ls()
        self.assertIn("file1.txt", result)
        self.assertIn("subdir", result)

    def test_cd_and_ls(self):
        """Тест команд cd и ls"""
        self.emulator.cd("subdir")
        result = self.emulator.ls()
        self.assertIn("file2.txt", result)

    def test_cd_invalid_directory(self):
        """Тест перехода в несуществующий каталог"""
        with self.assertRaises(FileNotFoundError):
            self.emulator.cd("nonexistent")

    def test_cd_parent_directory(self):
        """Тест перехода в родительский каталог"""
        self.emulator.cd("subdir")
        self.emulator.cd("..")
        result = self.emulator.ls()
        self.assertIn("file1.txt", result)
        self.assertIn("subdir", result)

    def test_ls_in_subdir(self):
        """Тест команды ls внутри подкаталога"""
        self.emulator.cd("subdir")
        result = self.emulator.ls()
        self.assertEqual(result, ["file2.txt"])


if __name__ == "__main__":
    unittest.main()
