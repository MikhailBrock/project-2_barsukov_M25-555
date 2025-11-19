import json
import os
from .constants import META_FILE, DATA_DIR

def load_metadata(filepath=META_FILE):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(data, filepath=META_FILE):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_data_dir():
    """Создает директорию data если она не существует."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_table_data(table_name):
    """Загружает данные таблицы из JSON-файла."""
    ensure_data_dir()
    filepath = f"{DATA_DIR}/{table_name}.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name, data):
    """Сохраняет данные таблицы в JSON-файл."""
    ensure_data_dir()
    filepath = f"{DATA_DIR}/{table_name}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
