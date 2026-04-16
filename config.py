# config.py
import os

# Базовый путь к внутреннему хранилищу
BASE_DIR = "/storage/emulated/0"

# Путь к проекту
PROJECT_DIR = os.path.join(BASE_DIR, "your PROJECT_DIR")

# Папка для загрузок
DOWNLOAD_DIR = os.path.join(BASE_DIR, "Download")

# Создаём папку, если её нет
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

TOKEN = "Your token"