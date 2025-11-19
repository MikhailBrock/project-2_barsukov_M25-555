"""Парсеры для сложных команд."""

import shlex
from .constants import VALID_TYPES

def parse_where_clause(where_str):
    """Парсит условие WHERE в формате 'столбец = значение'."""
    if not where_str:
        return None
    
    parts = where_str.split('=', 1)
    if len(parts) != 2:
        raise ValueError(f"Некорректный формат условия WHERE: {where_str}")
    
    column = parts[0].strip()
    value = parts[1].strip()
    
    # Убираем кавычки у строковых значений
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    
    return {column: value}

def parse_set_clause(set_str):
    """Парсит условие SET в формате 'столбец = значение'."""
    parts = set_str.split('=', 1)
    if len(parts) != 2:
        raise ValueError(f"Некорректный формат условия SET: {set_str}")
    
    column = parts[0].strip()
    value = parts[1].strip()
    
    # Убираем кавычки у строковых значений
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    
    return {column: value}

def parse_values(values_str):
    """Парсит значения для INSERT в формате '(значение1, значение2, ...)'."""
    if not values_str.startswith('(') or not values_str.endswith(')'):
        raise ValueError(f"Некорректный формат VALUES: {values_str}")
    
    # Убираем скобки и разбиваем по запятым
    values_content = values_str[1:-1].strip()
    if not values_content:
        return []
    
    # Используем shlex для корректного разбора значений с кавычками
    values = [v.strip() for v in shlex.split(values_content.replace(',', ' ')) if v.strip()]
    
    # Убираем кавычки у строковых значений
    parsed_values = []
    for value in values:
        if value.startswith('"') and value.endswith('"'):
            parsed_values.append(value[1:-1])
        elif value.startswith("'") and value.endswith("'"):
            parsed_values.append(value[1:-1])
        elif value.lower() == 'true':
            parsed_values.append(True)
        elif value.lower() == 'false':
            parsed_values.append(False)
        elif value.isdigit():
            parsed_values.append(int(value))
        else:
            parsed_values.append(value)
    
    return parsed_values

def validate_value_type(value, expected_type):
    """Проверяет соответствие значения ожидаемому типу."""
    if expected_type == "int":
        if not isinstance(value, int) and not (isinstance(value, str) and value.isdigit()):
            raise ValueError(f"Ожидается целое число, получено: {value}")
        return int(value)
    elif expected_type == "str":
        return str(value)
    elif expected_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ['true', '1']:
                return True
            elif value.lower() in ['false', '0']:
                return False
        raise ValueError(f"Ожидается булево значение, получено: {value}")
    else:
        raise ValueError(f"Неподдерживаемый тип: {expected_type}")
