import os
import shlex
import subprocess
import getpass
import socket

class ShellEmulator:
    def __init__(self):
        # Инициализация эмулятора
        self.running = True
        self.current_dir = os.getcwd()

    def get_prompt(self):
        """Формирование приглашения к вводу на основе реальных данных ОС"""
        # Получаем имя пользователя
        username = getpass.getuser()

        # Получаем имя хоста
        hostname = socket.gethostname()

        # Получаем текущую директорию и сокращаем домашнюю директорию до ~
        home_dir = os.path.expanduser("~")
        current_dir = os.getcwd()

        if current_dir.startswith(home_dir):
            # Заменяем путь домашней директории на ~
            display_dir = "~" + current_dir[len(home_dir):]
        else:
            display_dir = current_dir

        return f"{username}@{hostname}:{display_dir}$ "

    def parse_command(self, command_line):
        """Парсер командной строки с поддержкой переменных окружения"""
        try:
            # Разбиваем команду на аргументы с учетом кавычек
            args = shlex.split(command_line)

            # Заменяем переменные окружения на их значения
            parsed_args = []
            for arg in args:
                if arg.startswith('$'):
                    # Извлекаем имя переменной (убираем $)
                    var_name = arg[1:]
                    # Получаем значение переменной окружения или оставляем как есть, если не найдена
                    var_value = os.environ.get(var_name, arg)
                    parsed_args.append(var_value)
                else:
                    parsed_args.append(arg)

            return parsed_args
        except Exception as e:
            print(f"Ошибка парсинга: {e}")
            return []

    def expand_path(self, path):
        """Раскрытие специальных символов в путях"""
        # Заменяем ~ на домашнюю директорию
        if path.startswith('~'):
            path = os.path.expanduser(path)
        # Раскрываем переменные окружения в путях
        path = os.path.expandvars(path)
        return path

    def execute_command(self, args):
        """Выполнение команды"""
        if not args:
            return

        command = args[0]

        # Команда выхода
        if command == "exit":
            self.running = False
            print("Выход из эмулятора")

        # Команда ls - заглушка
        elif command == "ls":
            print(f"Команда: ls")
            if len(args) > 1:
                print(f"Аргументы: {args[1:]}")
            else:
                print("Аргументы: нет")

        # Команда cd - заглушка
        elif command == "cd":
            print(f"Команда: cd")
            if len(args) > 1:
                target_dir = self.expand_path(args[1])
                print(f"Аргумент: {target_dir}")
                # Здесь будет реальная смена директории на следующих этапах
            else:
                print("Аргументы: нет (переход в домашнюю директорию)")

        # Попытка выполнить системную команду
        else:
            try:
                # Пытаемся выполнить команду через системную оболочку
                result = subprocess.run(args, capture_output=True, text=True)
                if result.returncode == 0:
                    print(result.stdout, end='')
                else:
                    print(f"Ошибка выполнения команды: {command}")
                    print(result.stderr, end='')
            except FileNotFoundError:
                print(f"Неизвестная команда: {command}")
            except Exception as e:
                print(f"Ошибка при выполнении команды: {e}")

    def run(self):
        """Основной цикл REPL (Read-Eval-Print Loop)"""
        print("Добро пожаловать в эмулятор командной оболочки!")
        print("Доступные команды: ls, cd, exit")
        print("Поддерживаются переменные окружения ($HOME, $USER, etc.)")
        print("Для выхода введите 'exit'")
        print("-" * 50)

        while self.running:
            try:
                # Получаем приглашение и ждем ввод пользователя
                prompt = self.get_prompt()
                user_input = input(prompt).strip()

                # Пропускаем пустые строки
                if not user_input:
                    continue

                # Парсим команду
                args = self.parse_command(user_input)

                # Выполняем команду
                self.execute_command(args)

            except KeyboardInterrupt:
                print("\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход из эмулятора")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")

def main():
    """Точка входа в программу"""
    shell = ShellEmulator()
    shell.run()

if __name__ == "__main__":
    main()
