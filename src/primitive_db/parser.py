"""Парсеры для сложных команд."""

import shlex


def parse_where_clause(where_str):
    """Парсит условие WHERE в формате 'столбец оператор значение'."""
    if not where_str:
        return None

    # Поддерживаемые операторы сравнения
    operators = ['>=', '<=', '!=', '=', '>', '<']

    # Ищем оператор в строке
    operator = None
    for op in operators:
        if op in where_str:
            operator = op
            break

    if not operator:
        error_msg = f"Некорректный формат условия WHERE: {where_str}. "
        error_msg += f"Поддерживаемые операторы: {', '.join(operators)}"
        raise ValueError(error_msg)

    # Разбиваем строку на части
    parts = where_str.split(operator, 1)
    if len(parts) != 2:
        raise ValueError(f"Некорректный формат условия WHERE: {where_str}")

    column = parts[0].strip()
    value_str = parts[1].strip()

    # Убираем кавычки у строковых значений
    value = parse_value(value_str)

    return {'column': column, 'operator': operator, 'value': value}


def parse_set_clause(set_str):
    """Парсит условие SET в формате 'столбец = значение'."""
    parts = set_str.split('=', 1)
    if len(parts) != 2:
        raise ValueError(f"Некорректный формат условия SET: {set_str}")

    column = parts[0].strip()
    value_str = parts[1].strip()

    value = parse_value(value_str)

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
    values = [
        v.strip() for v in shlex.split(values_content.replace(',', ' '))
        if v.strip()
    ]

    # Парсим каждое значение
    parsed_values = []
    for value in values:
        parsed_values.append(parse_value(value))

    return parsed_values


def parse_value(value_str):
    """Парсит одиночное значение, преобразуя к правильному типу."""
    # Убираем кавычки у строковых значений
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    elif value_str.startswith("'") and value_str.endswith("'"):
        return value_str[1:-1]
    elif value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    elif value_str.isdigit():
        return int(value_str)
    elif value_str.replace('.', '').isdigit():  # Для дробных чисел
        return float(value_str)
    else:
        # Если не удалось определить тип, возвращаем как строку
        return value_str


def validate_value_type(value, expected_type):
    """Проверяет соответствие значения ожидаемому типу."""
    if expected_type == "int":
        if (not isinstance(value, int) and
                not (isinstance(value, str) and value.isdigit())):
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
        error_msg = f"Ожидается булево значение, получено: {value}"
        raise ValueError(error_msg)
    else:
        raise ValueError(f"Неподдерживаемый тип: {expected_type}")


def apply_where_condition(record, where_clause):
    """Применяет условие WHERE к записи."""
    if not where_clause:
        return True

    column = where_clause['column']
    operator = where_clause['operator']
    value = where_clause['value']

    record_value = record.get(column)

    # Если значения нет в записи, условие не выполняется
    if record_value is None:
        return False

    # Применяем оператор сравнения
    if operator == '=':
        return str(record_value) == str(value)
    elif operator == '!=':
        return str(record_value) != str(value)
    elif operator == '>':
        # Пытаемся сравнить как числа, если возможно
        try:
            return float(record_value) > float(value)
        except (ValueError, TypeError):
            return str(record_value) > str(value)
    elif operator == '<':
        try:
            return float(record_value) < float(value)
        except (ValueError, TypeError):
            return str(record_value) < str(value)
    elif operator == '>=':
        try:
            return float(record_value) >= float(value)
        except (ValueError, TypeError):
            return str(record_value) >= str(value)
    elif operator == '<=':
        try:
            return float(record_value) <= float(value)
        except (ValueError, TypeError):
            return str(record_value) <= str(value)
    else:
        return False