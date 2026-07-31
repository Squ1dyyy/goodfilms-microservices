# GoodFilms — Описание проекта и руководство по запуску

В данном файле представлено техническое описание платформы **GoodFilms**, ее архитектура, используемый стек технологий, список реализованного функционала и инструкции по запуску.

---

## 1. Описание проекта

**GoodFilms** — это микросервисная веб-платформа и каталог фильмов с векторными ИИ-рекомендациями. Проект объединяет возможности агрегатора контента (IMDb и TMDb), социальной платформы для киноманов (рецензии, оценки, комментарии) и сервиса персональных рекомендаций.

### Технологический стек:

#### Frontend
![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS_4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Radix UI](https://img.shields.io/badge/Radix_UI-161618?style=for-the-badge&logo=radix-ui&logoColor=white)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-0055FF?style=for-the-badge&logo=framer&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Vitest](https://img.shields.io/badge/Vitest-6E9F18?style=for-the-badge&logo=vitest&logoColor=white)

#### Backend & Async
![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37B24D?style=for-the-badge&logo=celery&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2.0-D71100?style=for-the-badge&logo=python&logoColor=white)

#### Databases & AI
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

#### Infrastructure & Gateway
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_&_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 2. Реализованный функционал

Текущая версия проекта включает полностью реализованный и протестированный функционал:

### 1. API Gateway (Nginx)
- Единая точка входа для всех микросервисов на порту `8080`.
- Rate limiting для защиты эндпоинтов от перегрузки.
- CORS и динамический DNS-резолвинг контейнеров Docker (`127.0.0.11`).
- Агрегированная Swagger/OpenAPI документация по адресу `/docs`.

### 2. Сервис авторизации (`auth`)
- Регистрация и вход с хешированием паролей (`bcrypt`).
- Генерация и валидация JWT-токенов (access и refresh).
- Учет активных сессий пользователей (с записью устройств, IP-адресов и User-Agent).
- Определение страны пользователя по IP через базу данных GeoIP (`GeoLite2-Country.mmdb`).

### 3. Сервис каталога фильмов (`movie`) и фоновые задачи (`Celery`)
- Структуры данных для фильмов, сериалов, актеров, режиссеров, жанров, стран, студий и тегов.
- Поиск и фильтрация по годам, рейтингам IMDb/TMDb, жанрам и типам медиа.
- **Автоматический ETL-пайплайн на Celery**:
  * Ежедневный автоматический импорт датасетов IMDb (`.tsv.gz`).
  * Автоматическое дополнение описаний и постеров из TMDb API.
  * Периодическая векторизация описаний фильмов.

### 4. Сервис умных рекомендаций (`recomendations`)
- Векторное хранилище на базе `pgvector` (`Vector(384)`).
- Генерация смысловых эмбеддингов для описаний фильмов.
- Семантический поиск похожих фильмов по косинусному расстоянию.

### 5. Сервис оценок и отзывов (`reviews`)
- Оценка фильмов по 10-балльной шкале.
- Создание развернутых текстовых рецензий.
- Система реакций (лайки и дизлайки) и ветка комментариев к рецензиям.

### 6. Сервис пользователей и закладок (`users`)
- Добавление фильмов в личные закладки пользователя.
- Подписки на актеров и режиссеров.

### 7. Сервис уведомлений (`notifications`)
- Сервис уведомлений со статусами (Pending, Sent, Read).
- FastStream и RabbitMQ для асинхронной обработки событий.

### 8. Панель администратора (`admin`)
- Графический интерфейс на SQLAdmin.
- Подключение админки ко всем базам данных микросервисов для управления контентом и пользователями.

### 9. Фронтенд (Next.js 15)
- Glassmorphism UI с темной темой и адаптивными анимациями.
- Страницы каталога, карточки фильмов, фильтры, отзывы и личный кабинет.
- Тестирование на Vitest (unit-тесты) и Playwright (E2E-тесты).

---

## 3. Планы по развитию проекта (Roadmap)

В будущих версиях планируется реализация следующего функционала:

### 1. Хранение медиа-файлов (S3 / MinIO)
- Перевод загрузки постеров и аватаров на собственное S3-хранилище (MinIO или Yandex Object Storage) для локального кэширования медиа-контента.

### 2. Авторизация через соцсети и 2FA
- Интеграция входа через Google OAuth2 и Yandex OAuth2.
- Двухфакторная аутентификация (2FA / TOTP) для аккаунтов администраторов и модераторов.

### 3. Real-Time уведомления (WebSockets)
- Подключение WebSockets для мгновенной доставки push-уведомлений на клиенте.

### 4. Гибридный рекомендательный движок
- Объединение векторного поиска по описаниям с алгоритмом коллаборативной фильтрации на основе оценок похожих пользователей.

### 5. Покрытие тестами (QA)
- Расширение покрытия бэкенда unit-тестами на Pytest.
- Добавление E2E-сценариев на Playwright для всех основных пользовательских путей.

### 6. Мониторинг и CI/CD
- Сбор ошибок через Sentry SDK.
- Метрики и дашборды в Prometheus + Grafana.
- Автоматизация сборки и тестирования в GitHub Actions.

---

## Руководство по запуску проекта

### 1. Подготовка конфигурации (.env)
```bash
cd backend
cp .env.example .env
```

### 2. Запуск контейнеров Docker Compose
```bash
docker-compose up --build -d
```

### 3. Применение миграций Alembic для всех баз данных
```bash
docker-compose exec auth alembic upgrade head
docker-compose exec movie alembic upgrade head
docker-compose exec reviews alembic upgrade head
docker-compose exec users alembic upgrade head
docker-compose exec recomendations alembic upgrade head
docker-compose exec notifications alembic upgrade head
```

### 4. Заполнение базы данных первичными данными (DB Seeding)

Чтобы запустить первоначальный импорт данных с IMDb, обогащение из TMDb и генерацию векторов, вызовите следующие команды:

```bash
# 1. Импорт датасетов IMDb (фильмы, рейтинги, персоны)
docker-compose exec movie-worker python -c "from movie.app.tasks.imdb_tasks import run_imdb_sync; run_imdb_sync()"

# 2. Добавление постеров и описаний из TMDb API
docker-compose exec movie-worker python -c "from movie.app.tasks.tmdb_tasks import run_tmdb_sync; run_tmdb_sync(only_missing=False)"

# 3. Генерация векторных эмбеддингов для ИИ-рекомендаций (pgvector)
docker-compose exec movie-worker python -c "from movie.app.tasks.embedding_tasks import sync_movie_embeddings; sync_movie_embeddings()"
```

### 5. Ссылки на запущенные сервисы
* **Фронтенд**: [http://localhost:8080](http://localhost:8080) (или `http://localhost:3000`)
* **API Gateway & Swagger Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)
* **Панель администратора (SQLAdmin)**: [http://localhost:8004](http://localhost:8004)
