# Mailing CRM

Django-сервис управления email-рассылками (Курсовой проект).

## 🚀 Функционал

### Часть 1: Базовый функционал
- Полный CRUD для клиентов, сообщений и рассылок.
- Динамическое обновление статуса рассылки (`update_status`).
- Отправка рассылок по требованию с проверкой временного окна.
- Логирование попыток отправки через `bulk_create`.
- Валидация дат в формах (начало не в прошлом, начало < окончания).
- Главная страница с базовой статистикой.

### Часть 2: Расширение функциональности
- **Аутентификация и регистрация**: Вход, выход, восстановление пароля и регистрация с подтверждением email (генерация токена и ссылка активации).
- **Статистика и отчеты**: Подсчет успешных/неуспешных попыток и процент доставки в деталях рассылки.
- **Ограничение доступа**: 
  - Пользователи управляют только своими данными (миксин `OwnerRequiredMixin`).
  - Менеджеры (`is_staff`) видят все данные, но не могут редактировать/удалять чужие записи.
- **Кеширование**: Настроено серверное кеширование через Redis (протокол RESP2) для главной страницы.
- **Профиль пользователя**: Возможность загрузки аватара, указания имени, фамилии и даты рождения.

## 🛠 Технологический стек
- Python 3.13+
- Django 6.1+
- PostgreSQL
- Redis (кеширование)
- Poetry (управление зависимостями)
- Bootstrap 5 + Montserrat (UI)

## ⚙️ Запуск проекта

1. Установите зависимости:
```bash
   poetry install
```
   
2. Примените миграции:

```bash
poetry run python manage.py migrate
```
3. Запустите сервер Redis (если используется локально).

4. Запустите сервер разработки:

```bash
      poetry run python manage.py runserver
```

# Структура проекта Mailing CRM

<details>
<summary>Нажми, чтобы посмотреть структуру файлов</summary>

```
mailing_crm/
├── config/ # Настройки Django проекта
│ ├── init.py
│ ├── asgi.py # ASGI конфигурация
│ ├── settings.py # Основные настройки проекта
│ ├── urls.py # Корневые URL маршруты
│ ── wsgi.py # WSGI конфигурация
│
├── mailings/ # Основное приложение
│ ├── migrations/ # Миграции базы данных
│ │ ├── 0001_initial.py # Начальная миграция (Client, Message, Mailing, MailingAttempt)
│ │ ├── 0002_profile.py # Миграция для модели Profile
│ │ └── init.py
│ │
│ ├── templates/mailings/ # HTML шаблоны
│ │ ├── base.html # Базовый шаблон (навигация, стили)
│ │ ├── home.html # Главная страница
│ │ ├── client_list.html # Список клиентов
│ │ ├── client_form.html # Форма создания/редактирования клиента
│ │ ├── client_confirm_delete.html # Подтверждение удаления клиента
│ │ ├── message_list.html # Список сообщений
│ │ ├── message_form.html # Форма создания/редактирования сообщения
│ │ ├── message_confirm_delete.html # Подтверждение удаления сообщения
│ │ ├── mailing_list.html # Список рассылок
│ │ ├── mailing_detail.html # Детальная информация о рассылке
│ │ ├── mailing_form.html # Форма создания/редактирования рассылки
│ │ ├── mailing_confirm_delete.html # Подтверждение удаления рассылки
│ │ ├── login.html # Страница входа
│ │ ├── register.html # Страница регистрации
│ │ ├── register_success.html # Успешная регистрация
│ │ ├── activate_success.html # Успешная активация аккаунта
│ │ ├── activate_invalid.html # Ошибка активации
│ │ ├── password_reset.html # Сброс пароля
│ │ ├── password_reset_done.html # Подтверждение сброса пароля
│ │ ├── password_reset_confirm.html # Ввод нового пароля
│ │ ├── password_reset_complete.html # Пароль изменён
│ │ ├── profile.html # Профиль пользователя
│ │ ── profile_edit.html # Редактирование профиля
│ │
│ ├── init.py
│ ├── admin.py # Регистрация моделей в админке
│ ├── apps.py # Конфигурация приложения
│ ├── forms.py # Django формы (ClientForm, MessageForm, MailingForm, RegisterForm, ProfileForm)
│ ├── middleware.py # Middleware для очистки кэша при входе/выходе
│ ├── mixins.py # Миксины (OwnerRequiredMixin для ограничения доступа)
│ ├── models.py # Модели данных (Client, Message, Mailing, MailingAttempt, Profile)
│ ├── tests.py # ТЕСТЫ (покрытие views, models, forms)
│ ├── urls.py # URL маршруты приложения
│ └── views.py # View классы (CRUD, аутентификация, профиль, статистика)
│
├── media/ # Загруженные файлы (аватарки пользователей)
│ └── avatars/ # Папка с аватарами
│
├── .env # Переменные окружения (SECRET_KEY, DB credentials, EMAIL settings)
├── .env.example # Пример .env файла
├── .gitignore # Игнорируемые файлы Git
├── manage.py # Django management script
├── poetry.lock # Зафиксированные зависимости Poetry
├── pyproject.toml # Конфигурация Poetry (зависимости: Django, PostgreSQL, Redis, Pillow)
└── README.md # Документация проекта
```
</details>

## 👤 Роли

- Пользователь: управляет своими клиентами и рассылками.
- Модератор/Администратор (is_staff): имеет расширенные права просмотра в интерфейсе и полный контроль через Django Admin.

## 👨‍💻 Автор
Дмитрий Леонтьев (DiamondDim)
© 2026
## 📄 Лицензия
MIT — Учебный проект для курса Python-разработки Skypro.