### Hexlet tests and linter status:
[![Actions Status](https://github.com/KlyaksaOFF/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/KlyaksaOFF/python-project-52/actions)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=KlyaksaOFF_python-project-52&metric=coverage)](https://sonarcloud.io/summary/new_code?id=KlyaksaOFF_python-project-52)
# Python Project "Task Manager"

**Менеджер задач** — это полнофункциональное веб-приложение на Django для управления делами в команде.

### Возможности
- Регистрация и аутентификация пользователей.
- Создание, редактирование и удаление задач.
- Управление статусами задач и метками (Labels).
- Гибкая фильтрация списка задач по исполнителю, статусу и меткам.

### Технологии
- **Язык:** Python
- **Фреймворк:** Django (шаблоны, ORM, аутентификация)
- **База данных:** PostgreSQL (prod), SQLite (dev)
- **Стили:** Bootstrap 5
- **Инструменты:** Makefile, Ruff linter,  Django tests

### Быстрый старт

1. **Клонируйте репозиторий:**
   ```bash
   git clone [https://github.com/KlyaksaOFF/python-project-52.git](https://github.com/KlyaksaOFF/python-project-52.git)
   cd python-project-52
   
2. **Настройте окружение:**
    ```bash
   Создайте файл .env в корне проекта.
   Добавьте необходимые переменные (SECRET_KEY, DATABASE_URL).
3. **Makefile + Установка зависимостей**
    ```bash
    make install
    make migrate
    make start