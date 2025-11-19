"""Основной цикл программы и обработка команд."""

import prompt
import shlex
from .utils import load_metadata, save_metadata
from .core import (
    create_table, drop_table, list_tables, 
    insert, select, update, delete, info
)
from .parser import parse_where_clause, parse_set_clause, parse_values

def print_help():
    """Выводит справочную информацию."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nУправление таблицами:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    """Основной цикл программы."""
    print("***База данных***")
    print_help()
    
    while True:
        try:
            user_input = prompt.string(">>>Введите команду: ")
            if not user_input:
                continue
                
            args = shlex.split(user_input)
            command = args[0].lower()
            
            if command == "exit":
                break
            elif command == "help":
                print_help()
            
            # Команды управления таблицами
            elif command == "create_table":
                if len(args) < 3:
                    print("Ошибка: Недостаточно аргументов. Используйте: create_table <имя_таблицы> <столбец1:тип> ...")
                    continue
                
                metadata = load_metadata()
                metadata = create_table(metadata, args[1], args[2:])
                save_metadata(metadata)
                
            elif command == "list_tables":
                metadata = load_metadata()
                list_tables(metadata)
                
            elif command == "drop_table":
                if len(args) < 2:
                    print("Ошибка: Недостаточно аргументов. Используйте: drop_table <имя_таблицы>")
                    continue
                
                metadata = load_metadata()
                metadata = drop_table(metadata, args[1])
                save_metadata(metadata)
            
            # CRUD операции
            elif command == "insert":
                if len(args) < 5 or args[1].lower() != "into" or args[3].lower() != "values":
                    print("Ошибка: Некорректный формат. Используйте: insert into <таблица> values (<значения>)")
                    continue
                
                table_name = args[2]
                values_str = ' '.join(args[4:])
                
                try:
                    values = parse_values(values_str)
                    metadata = load_metadata()
                    insert(metadata, table_name, values)
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif command == "select":
                if len(args) < 3 or args[1].lower() != "from":
                    print("Ошибка: Некорректный формат. Используйте: select from <таблица> [where условие]")
                    continue
                
                table_name = args[2]
                where_clause = None
                
                # Обработка условия WHERE
                if len(args) > 4 and args[3].lower() == "where":
                    where_str = ' '.join(args[4:])
                    try:
                        where_clause = parse_where_clause(where_str)
                    except Exception as e:
                        print(f"Ошибка в условии WHERE: {e}")
                        continue
                
                try:
                    metadata = load_metadata()
                    select(metadata, table_name, where_clause)
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif command == "update":
                if len(args) < 7 or args[2].lower() != "set" or "where" not in [arg.lower() for arg in args]:
                    print("Ошибка: Некорректный формат. Используйте: update <таблица> set <столбец>=<значение> where <условие>")
                    continue
                
                table_name = args[1]
                
                # Находим индекс WHERE
                where_index = next(i for i, arg in enumerate(args) if arg.lower() == "where")
                
                set_str = ' '.join(args[3:where_index])
                where_str = ' '.join(args[where_index + 1:])
                
                try:
                    set_clause = parse_set_clause(set_str)
                    where_clause = parse_where_clause(where_str)
                    
                    metadata = load_metadata()
                    update(metadata, table_name, set_clause, where_clause)
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif command == "delete":
                if len(args) < 5 or args[1].lower() != "from" or args[3].lower() != "where":
                    print("Ошибка: Некорректный формат. Используйте: delete from <таблица> where <условие>")
                    continue
                
                table_name = args[2]
                where_str = ' '.join(args[4:])
                
                try:
                    where_clause = parse_where_clause(where_str)
                    metadata = load_metadata()
                    delete(metadata, table_name, where_clause)
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif command == "info":
                if len(args) < 2:
                    print("Ошибка: Недостаточно аргументов. Используйте: info <имя_таблицы>")
                    continue
                
                try:
                    metadata = load_metadata()
                    info(metadata, args[1])
                except Exception as e:
                    print(f"Ошибка: {e}")
                
            else:
                print(f"Функции {command} нет. Попробуйте снова.")
                
        except Exception as e:
            print(f"Произошла ошибка: {e}")
