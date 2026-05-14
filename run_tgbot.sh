#!/usr/bin/env bash

SESSION_NAME="tg_fuck_spam_bot"
WORK_DIR="/storage/emulated/0/ВАШ_ПУТЬ_К_ФАЙЛАМ"

# 1. Попытка вывести приложение Termux на передний план
# Работает, если приложение не убито полностью (висит в фоне)
am start -n com.termux/com.termux.app.TermuxActivity > /dev/null 2>&1

# 2. Блокировка сна (критично для работы в фоне)
termux-wake-lock

# 3. Убиваем старую сессию, если есть
tmux kill-session -t "$SESSION_NAME" 2>/dev/null

# 4. Запускаем новую сессию в фоне
tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR" "python3 bot.py"

# 5. Подключаемся к сессии (чтобы видеть окно и логи)
tmux attach -t "$SESSION_NAME"
