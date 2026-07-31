# GoodFilms Frontend

Красивый и отзывчивый веб-интерфейс на Next.js App Router для каталога фильмов "GoodFilms". Использует стек современных технологий для обеспечения высокого уровня интерактивности (эффекты стекла, плавные переходы, анимации) и надежной работы с данными.

## 🚀 Стек технологий

- **Фреймворк**: Next.js 15+ (App Router)
- **Стилизация**: Tailwind CSS 4, Glassmorphism, CSS Variables
- **Анимации**: Framer Motion, GSAP
- **Управление состоянием**: Zustand (сессии, локальное хранилище), TanStack Query / React Query (кэширование серверных данных)
- **Формы и валидация**: React Hook Form, Zod
- **Компоненты**: Radix UI Primitives (Dialog, DropdownMenu, Tabs, Toast)
- **Тестирование**: Vitest + React Testing Library (юнит-тесты), Playwright (E2E-тесты)

---

## 🛠 Установка и запуск локально

### 1. Подготовка окружения
Убедитесь, что у вас установлен Node.js версии 18 или новее.

Создайте файл `.env.local` в корне папки `frontend` на основе примера:
```bash
cp .env.example .env.local
```

Переменные окружения по умолчанию:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api/v1  # Gateway API бэкенда
FEATURE_RECOMMENDATIONS=false                          # Feature-flag для рекомендаций
FEATURE_REVIEWS=false                                  # Feature-flag для отзывов
NEXT_PUBLIC_APP_URL=http://localhost:3000              # URL нашего приложения
```

### 2. Установка зависимостей
```bash
npm install
```

### 3. Запуск сервера разработки
```bash
npm run dev
```
Откройте [http://localhost:3000](http://localhost:3000) для просмотра приложения в браузере.

---

## 🧪 Тестирование

### Запуск Unit-тестов (Vitest)
Запуск тестов для проверки хуков авторизации, закладок, уведомлений и HTTP-клиента:
```bash
npm run test
```

### Запуск E2E-тестов (Playwright)
Перед первым запуском необходимо установить браузер Playwright:
```bash
npx playwright install chromium
```

Запустите сквозные тесты:
```bash
npx playwright test
```

---

## 🐳 Деплой и Docker

Проект настроен на сборку в режиме `standalone` для уменьшения размера Docker-образа.

### Сборка Docker-образа вручную
В корневой папке `frontend` выполните:
```bash
docker build -t goodfilms-frontend .
```

### Интеграция с Docker Compose бэкенда
Фронтенд полностью интегрирован в общую Docker-сеть бэкенда. Сервис `frontend` автоматически запускается в `backend/docker-compose.yml` и проксируется через Gateway (Nginx) по корневому пути `/`.

Для запуска всей системы (бэкенд + фронтенд):
```bash
cd ../backend
docker-compose up --build -d
```
После успешного запуска проект будет доступен на порту `8080` (Gateway):
- Фронтенд: [http://localhost:8080](http://localhost:8080)
- API Gateway: [http://localhost:8080/api/v1](http://localhost:8080/api/v1)
