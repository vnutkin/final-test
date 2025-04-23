import os
from pathlib import Path

# Настройки
ROOT_DIR = Path("D:/github/final-test/flower_delivery")  # Путь к проекту
OUTPUT_FILE = "project_code.txt"  # Итоговый файл
EXCLUDE = {  # Исключаемые элементы
    'venv', '__pycache__', '.git', 'migrations',
    '.idea', 'node_modules', 'staticfiles', 'media', 'unload.py'
}
EXCLUDE_EXTENSIONS = {  # Исключаемые расширения
    '.pyc', '.pyo', '.pyd', '.db', '.sqlite3', '.env', '.log', '.txt'  # Добавлена точка перед txt
}

def should_include(filepath):
    """Проверка, нужно ли включать файл"""
    parts = filepath.parts
    return (
        not any(part in EXCLUDE for part in parts) and
        filepath.suffix not in EXCLUDE_EXTENSIONS and
        not filepath.name.startswith('.')
    )

with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk(ROOT_DIR):
        root_path = Path(root)
        for file in files:
            file_path = root_path / file
            if should_include(file_path):
                try:
                    # Заголовок с относительным путем
                    rel_path = file_path.relative_to(ROOT_DIR)
                    outfile.write(f"\n\n=== FILE: {rel_path} ===\n\n")

                    # Чтение файла в бинарном режиме и декодирование с обработкой ошибок
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='replace')
                        outfile.write(content)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
