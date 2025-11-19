"""Основная логика работы с таблицами и данными."""

from prettytable import PrettyTable
from .utils import load_table_data, save_table_data
from .parser import validate_value_type, parse_where_clause, parse_set_clause
from .constants import VALID_TYPES
from .decorators import handle_db_errors, confirm_action, log_time, simple_cache

@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает новую таблицу."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    
    # Добавляем ID столбец автоматически
    table_columns = ["ID:int"]
    table_columns.extend(columns)
    
    # Проверяем типы данных
    for col in table_columns:
        col_parts = col.split(":")
        if len(col_parts) != 2:
            print(f'Ошибка: Некорректный формат столбца "{col}". Используйте: имя:тип')
            return metadata
        
        col_name, col_type = col_parts
        if col_type not in VALID_TYPES:
            print(f'Ошибка: Неподдерживаемый тип данных "{col_type}" в столбце "{col_name}".')
            return metadata
    
    metadata[table_name] = table_columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(table_columns)}')
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

@handle_db_errors
def list_tables(metadata):
    """Выводит список всех таблиц."""
    if not metadata:
        print("Нет созданных таблиц.")
        return
    
    print("Список таблиц:")
    for table_name in metadata:
        print(f"- {table_name}")

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет запись в таблицу."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    
    table_data = load_table_data(table_name)
    columns = metadata[table_name]
    
    # Проверяем количество значений (без ID)
    if len(values) != len(columns) - 1:
        raise ValueError(f'Ожидается {len(columns) - 1} значений, получено {len(values)}')
    
    # Генерируем ID
    new_id = 1
    if table_data:
        new_id = max(record.get('ID', 0) for record in table_data) + 1
    
    # Создаем запись
    record = {'ID': new_id}
    for i, col in enumerate(columns[1:]):  # Пропускаем ID
        col_name, col_type = col.split(":")
        record[col_name] = validate_value_type(values[i], col_type)
    
    table_data.append(record)
    save_table_data(table_name, table_data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data

@handle_db_errors
@log_time
@simple_cache
def select(metadata, table_name, where_clause=None):
    """Выбирает записи из таблицы."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    
    table_data = load_table_data(table_name)
    
    if not table_data:
        print(f'Таблица "{table_name}" пуста.')
        return []
    
    # Фильтруем записи если задано условие
    if where_clause:
        filtered_data = []
        for record in table_data:
            match = True
            for col, value in where_clause.items():
                if str(record.get(col, '')) != str(value):
                    match = False
                    break
            if match:
                filtered_data.append(record)
        result_data = filtered_data
    else:
        result_data = table_data
    
    # Выводим результат в виде таблицы
    if result_data:
        columns = [col.split(":")[0] for col in metadata[table_name]]
        table = PrettyTable()
        table.field_names = columns
        
        for record in result_data:
            row = [record.get(col, '') for col in columns]
            table.add_row(row)
        
        print(table)
    else:
        print("Записи не найдены.")
    
    return result_data

@handle_db_errors
def update(metadata, table_name, set_clause, where_clause):
    """Обновляет записи в таблице."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    
    table_data = load_table_data(table_name)
    columns_dict = {col.split(":")[0]: col.split(":")[1] for col in metadata[table_name]}
    
    updated_count = 0
    for record in table_data:
        match = True
        # Проверяем условие WHERE
        if where_clause:
            for col, value in where_clause.items():
                if str(record.get(col, '')) != str(value):
                    match = False
                    break
        
        if match:
            # Обновляем поля согласно SET
            for col, new_value in set_clause.items():
                if col in columns_dict:
                    record[col] = validate_value_type(new_value, columns_dict[col])
                    updated_count += 1
    
    if updated_count > 0:
        save_table_data(table_name, table_data)
        print(f'Успешно обновлено {updated_count} записей в таблице "{table_name}".')
    else:
        print("Записи для обновления не найдены.")
    
    return table_data

@handle_db_errors
@confirm_action("удаление записей")
def delete(metadata, table_name, where_clause):
    """Удаляет записи из таблицы."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    
    table_data = load_table_data(table_name)
    
    # Фильтруем записи которые НЕ должны быть удалены
    filtered_data = []
    deleted_count = 0
    
    for record in table_data:
        match = True
        if where_clause:
            for col, value in where_clause.items():
                if str(record.get(col, '')) != str(value):
                    match = False
                    break
        
        if match:
            deleted_count += 1
        else:
            filtered_data.append(record)
    
    if deleted_count > 0:
        save_table_data(table_name, filtered_data)
        print(f'Успешно удалено {deleted_count} записей из таблицы "{table_name}".')
    else:
        print("Записи для удаления не найдены.")
    
    return filtered_data

@handle_db_errors
def info(metadata, table_name):
    """Выводит информацию о таблице."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    
    table_data = load_table_data(table_name)
    
    print(f'Таблица: {table_name}')
    print(f'Столбцы: {", ".join(metadata[table_name])}')
    print(f'Количество записей: {len(table_data)}')
