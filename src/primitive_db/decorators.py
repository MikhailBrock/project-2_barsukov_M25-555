"""Декораторы для улучшения кода"""

import time

import prompt


def handle_db_errors(func):
    """Декоратор для обработки ошибок базы данных"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    """Декоратор для подтверждения опасных операций"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            confirmation = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if confirmation.lower() == 'y':
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")
                return None
        return wrapper
    return decorator


def log_time(func):
    """Декоратор для замера времени выполнения функции"""
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.3f} секунд.")
        return result
    return wrapper


# Простое кэширование для демонстрации
_simple_cache = {}


def simple_cache(func):
    """Простой декоратор для кэширования"""
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
        if cache_key in _simple_cache:
            print("(результат из кэша)")
            return _simple_cache[cache_key]
        else:
            result = func(*args, **kwargs)
            _simple_cache[cache_key] = result
            return result
    return wrapper