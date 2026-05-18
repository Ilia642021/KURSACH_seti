#!/bin/bash

# Очистка старой инициализации, если она была
rm -rf .git

# Настройка локального пользователя для этого репозитория
git init
git config user.name "Ilia642021"
git config user.email "ilia.a.yakovenko@gmail.com"

# Добавление всех файлов (с учетом .gitignore)
git add .

# Первый коммит
git commit -m "Initial commit: OMNeT++ project for Ilia642021"

# Инструкция для пользователя
echo "--------------------------------------------------------"
echo "Репозиторий инициализирован локально для Ilia642021."
echo "--------------------------------------------------------"
echo "ВАЖНО: GitHub больше не принимает обычные пароли в терминале."
echo "Твой пароль 'mD2-PxX-sNm-r8r' выглядит как Personal Access Token (PAT)."
echo ""
echo "Чтобы отправить код, выполни эти команды в терминале ТВОЕЙ СИСТЕМЫ:"
echo "(замени <TOKEN> на твой пароль/токен, если он не подставится автоматически)"
echo ""
echo "1. Привязка удаленного репозитория:"
echo "   git remote add origin https://Ilia642021:mD2-PxX-sNm-r8r@github.com/Ilia642021/KURSACH_seti.git"
echo ""
echo "2. Отправка кода:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo "--------------------------------------------------------"
