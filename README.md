# FSB - FuckSpamBot
Загрузчик видео с ютуб.
Тот случай когда устал от рекламы в аналогичных ботах настолько, что начал изучать программирование и делать своих ботов)
Не обошолся без использования нейросетей (Qwen), но я учусь, а результат мне нужен был здесь и сейчас.

## Оглавление
- [Требования](#-требования)
- [Установка](#-установка)
- [Использование](#-использование)

## Требования

- **Android 7.0+** (API 24+)
- **Termux, Termux:Widget** (устанавливать только с F-Droid)
- **Python 3.10+** (поставляется с Termux)

## Установка

### 1. Подготовка окружения

# Обновите пакеты и установите зависимости
pkg update && pkg upgrade
pkg install python git clang libffi openssl rust
# Клонируйте репозиторий в домашнюю директорию Termux
# Проверить все файлы config и run_tgbot.sh и прописать свои пути и токены
# Установите зависимости
pip install -r requirements.txt

# Убедитесь, что скрипты исполняемые
chmod +x scripts/*.py
chmod +x widgets/*.sh

# Настройте права для директорий виджетов (обязательно для Termux:Widget)
mkdir -p ~/.shortcuts ~/.shortcuts/tasks ~/.shortcuts/icons
chmod 700 -R ~/.shortcuts

## Использование
# Работает как по ссылке с ютуба, предлагая скачать в качестве 360, 480, 720, 1080, аудио:

<img width="1080" height="2316" alt="1" src="https://github.com/user-attachments/assets/ea389213-0ea2-4441-a224-e9604f0c2081" />
<img width="1080" height="2316" alt="2" src="https://github.com/user-attachments/assets/ea8955c8-b472-4ea0-ad63-da035134878e" />

# Так и по алгоритму поиска, выдавая первые 10 популярных результатов:

<img width="1080" height="2316" alt="3" src="https://github.com/user-attachments/assets/32c2d55a-1b28-4e0f-ac5a-5195907ce5cd" />
<img width="1080" height="2316" alt="4" src="https://github.com/user-attachments/assets/478b40ff-c268-422b-b273-b3f5e6e0f4d4" />
<img width="1080" height="2316" alt="5" src="https://github.com/user-attachments/assets/9977bee1-9428-4e3f-96f1-8bafd2e0d25d" />
