# GoodFilms — Execution Plan для автономного AI-агента

> Этот документ предназначен для автономного выполнения AI-агентом (например, Claude Code). Формат — последовательность атомарных задач с явными зависимостями, точными контрактами и проверяемым Definition of Done. Это **не** заменяет ТЗ для людей (`GoodFilms_TZ_i_plan_razrabotki.md`) — это инструкция к действию.

---

## 0. Правила выполнения (обязательны для агента)

1. **Backend не трогать.** Backend полностью готов и задеплоен. Запрещено создавать, изменять или предлагать новые backend-эндпоинты. Все обращения — только к маршрутам из раздела «1. Контракты API» этого документа.
2. **Не задавать вопросы пользователю.** Если в задаче не зафиксировано конкретное значение (текст, иконка, точный px) — принять разумное решение самостоятельно по принципам из §4 «Дизайн-токены» и продолжить выполнение.
3. **Выполнять задачи по порядку ID**, не пропускать зависимости (`Зависит от:`).
4. После каждой задачи: `npm run lint && npm run typecheck && npm run build` — задача не считается выполненной, если эти команды падают.
5. Коммит после каждой задачи: `feat(TASK-ID): краткое описание на русском`.
6. Не использовать параметры/эндпоинты, которых нет в контрактах ниже, даже если они кажутся «логичными» (например, у `/movies` нет параметра сортировки — не добавлять его).
7. Все переменные окружения — через `.env.local`, базовый пример — в `.env.example` (создаётся в TASK-A04).
8. Каждая задача завершается самопроверкой по чек-листу Definition of Done (DoD) перед переходом к следующей.

---

## 1. Контракты API (фиксированные, источник — `api.md`)

Базовый URL: `process.env.NEXT_PUBLIC_API_BASE_URL` (например `http://localhost:8080/api/v1`). Gateway уже существует, фронтенд только потребляет его.

### 1.1 Auth Service
| Действие | Метод/путь | Тело запроса | Ответ | Auth |
|---|---|---|---|---|
| Регистрация | `POST /auth/register` | `{email, username, password, password_confirm}` | `201` `TokenResponseSchema` | нет |
| Вход | `POST /auth/login` | `{email, password}` | `200` `TokenResponseSchema` | нет |
| Обновление токена | `POST /auth/refresh` | `{refresh_token}` | `200` `TokenResponseSchema` | нет |
| Выход | `POST /auth/logout` | `{refresh_token}` | `204` | Bearer |
| Текущий пользователь | `GET /auth/me` | — | `200` `UserDataSchema` | Bearer |
| Забыли пароль | `POST /auth/forgot_password` | `{email}` | `200` `{status}` | нет (rate-limit) |
| Проверка токена сброса | `GET /auth/reset_password?token=` | — | `200` `{status}` | нет |
| Установка пароля | `POST /auth/reset_password?token=` | `{new_password}` | `200` `{status}` | нет |
| Подтверждение email | `POST /auth/verify_email?code=` | — | `200` `{status}` | нет (rate-limit) |
| Повторный код | `POST /auth/send_verification` | — | `200` `{status}` | Bearer (rate-limit) |
| Смена пароля | `PATCH /auth/password` | `{current_password, new_password, new_password_confirm}` | `200` `TokenResponseSchema` | Bearer |
| Список сессий | `GET /auth/sessions` | — | `200` `SessionSchema[]` | Bearer |
| Закрыть все, кроме текущей | `DELETE /auth/sessions/all` | — | `204` | Bearer |
| Закрыть сессию | `DELETE /auth/sessions/{session_id}` | — | `204` | Bearer |

```ts
// types/auth.ts
interface TokenResponseSchema { access_token: string; token_type: "bearer"; refresh_token: string; user: UserPublicSchema }
interface UserPublicSchema { id: number; username: string }
interface UserDataSchema { id: number; username: string; email: string; is_active: boolean; is_verified: boolean; role: string }
interface SessionSchema { id: number; device_name?: string; device_type?: string; user_agent?: string; ip_address?: string; country?: string }
```

### 1.2 Movie Catalog Service
| Действие | Метод/путь | Query-параметры (других НЕТ) |
|---|---|---|
| Список фильмов | `GET /movies` | `page, limit(≤50), genre_id, country_id, studio_id, year_from, year_to, search` |
| Карточка фильма | `GET /movies/{movie_id}` | — |
| Список персон | `GET /persons` | `page, limit, search` |
| Карточка персоны | `GET /persons/{person_id}` | — (ответ включает `movies` с пагинацией) |
| Жанры/студии/страны | `GET /genres`, `GET /studios`, `GET /countries` | — (полный список без пагинации) |

```ts
// types/movie.ts
interface MovieListItem { id: number; title: string; release_year: number; poster_url: string; genres: string[] }
interface MovieListResponse { items: MovieListItem[]; total: number; page: number; limit: number }
interface CastMember { person_id: number; full_name: string; photo_url: string; character_name: string; billing_order: number }
interface MovieDetail extends Omit<MovieListItem,'genres'> {
  description: string; genres: string[]; studios: string[];
  cast: CastMember[]; directors: unknown[]; writers: unknown[]; producers: unknown[];
}
interface Person { id: number; full_name: string; birth_date: string; photo_url: string }
interface PersonDetailResponse { person: Person; movies: MovieListResponse }
interface RefItem { id: number; name: string } // Genre / Studio / Country
```

### 1.3 Users Service
| Действие | Метод/путь | Статус |
|---|---|---|
| Закладки (список id) | `GET /users/me/bookmarks` | готово, отдаёт `number[]` |
| Добавить закладку | `POST /users/me/bookmarks/{movie_id}` | готово |
| Удалить закладку | `DELETE /users/me/bookmarks/{movie_id}` | готово |
| Подписаться на персону | `POST /users/subscribe/person/{person_id}` | готово |
| Отписаться | `DELETE /users/subscribe/person/{person_id}` | готово |
| Мои подписки (список id) | `GET /users/subscribe/person` | готово |
| Профиль (чужой/свой) | `GET /users/{id}/profile`, `PATCH /users/me/profile` | **заглушка `{"detail":"Not implemented"}`** |
| История просмотров | `GET/POST /users/me/history*` | **заглушка** |

> Закладки отдают только `number[]`. Для отображения карточек — отдельный `GET /movies/{id}` на каждый id, через `useQueries` (React Query), с общим кэшем по ключу `["movie", id]`, чтобы не дублировать запросы с каталогом.

### 1.4 Notifications Service
| Действие | Метод/путь |
|---|---|
| Список | `GET /notification?page=&limit=` |
| Прочитать одно | `PATCH /notification/{id}/read` |
| Прочитать все | `POST /notification/read-all` |
| Удалить | `DELETE /notification/{id}` |

```ts
interface NotificationItem {
  id: number;
  type: "email_verification" | "password_reset" | "welcome" | "new_movie";
  url_link: string;
  status: "pending_movie" | "pending_delivery" | "delivered";
  created_at: string;
}
```

### 1.5 Recommendations / Reviews — заглушки
Любой вызов `*/recommendations*` и `*/reviews*` отдаёт `{"detail": "Not implemented"}`. Реализовать вызовы, но рендерить результат только за feature-флагом (см. TASK-H01). Не блокировать остальной UI ошибкой, если эндпоинт вернул заглушку.

### 1.6 Коды ошибок (единая обработка)
`400/401/403/404/429` → тело `{"detail": string}`. Единый перехватчик в API-клиенте должен пробрасывать `detail` в UI-уведомление об ошибке; `401` обрабатывается отдельно (см. TASK-B07); `429` показывает таймер повтора, если в ответе есть информация о лимите.

---

## 2. Зафиксированный технологический стек (не менять без явной причины)

```bash
npx create-next-app@latest goodfilms --typescript --tailwind --app --eslint
cd goodfilms
npm install @tanstack/react-query zustand axios react-hook-form zod @hookform/resolvers
npm install framer-motion gsap lucide-react
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tabs @radix-ui/react-toast
npm install -D vitest @testing-library/react @testing-library/jest-dom @playwright/test prettier
```

Не добавлять альтернативные UI-киты, альтернативные state-менеджеры или альтернативные http-клиенты — это создаёт несогласованность для последующих задач, которые ссылаются на конкретные API этих библиотек.

---

## 3. Структура проекта (создать ровно так)

```
src/
  app/
    (auth)/login/page.tsx
    (auth)/register/page.tsx
    (auth)/forgot-password/page.tsx
    (auth)/reset-password/page.tsx
    (auth)/verify-email/page.tsx
    movies/page.tsx
    movies/[id]/page.tsx
    persons/[id]/page.tsx
    search/page.tsx
    favorites/page.tsx
    notifications/page.tsx
    profile/page.tsx
    profile/sessions/page.tsx
    watch-links/[movieId]/route.ts
    go/[providerId]/[movieId]/route.ts
    sitemap.ts
    layout.tsx
    page.tsx
  components/
    ui/            # Button, Dialog, DropdownMenu, Tabs, Toast (обёртки над Radix)
    glass/          # GlassCard, GlassPanel, LiquidBlobBackground, ShimmerSkeleton
    movie/          # MovieCard, MovieGrid, MovieFilters, WatchProvidersRow
    person/
    notifications/
    layout/         # Header, Footer, NavGlass, NotificationBell
  features/
    auth/
    movies/
    favorites/
    notifications/
    watchLinks/
  lib/
    api-client.ts
    query-client.ts
    feature-flags.ts
    formatters.ts
  styles/
    tokens.css
    glass.css
  data/
    watch-providers.ts
    watch-links.json
  hooks/
  store/
  types/
  tests/
```

---

## 4. Дизайн-токены (создать файлы как есть, значения не менять без явной задачи)

```css
/* styles/tokens.css */
:root {
  --bg-void: #0A0C14;
  --bg-blob-violet: #6E5CFF;
  --bg-blob-cyan: #33D4C8;
  --glass-surface: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.14);
  --accent-gold: #E8B74C;
  --font-display: "Clash Display", "General Sans", sans-serif;
  --font-body: "Inter", sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}
```

```css
/* styles/glass.css */
.glass-surface {
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(24px) saturate(160%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.25);
}
```

Правило контраста (обязательно во всех компонентах с текстом на стекле): текст всегда располагается на тёмной подложке-градиенте (`linear-gradient(to top, var(--bg-void), transparent)`) внутри стеклянной карточки, не напрямую на прозрачном фоне. Максимум 2 стеклянные поверхности друг над другом одновременно.

Анимационные параметры (использовать именно эти значения, без вариаций между компонентами):
- переход между страницами: crossfade + blur, `200–250ms`, easing `cubic-bezier(0.4,0,0.2,1)`;
- hover-tilt карточки: `rotateX/rotateY` в диапазоне `±6deg` по позиции курсора;
- liquid-light-leak (сигнатурный эффект): блок размером `~480px`, blur `60px`, плавно следует за курсором с задержкой через `lerp` (коэффициент `0.08`) — НЕ мгновенно;
- все анимации оборачиваются проверкой `prefers-reduced-motion: reduce` → fallback на simple opacity fade `150ms`.

---

## 5. Задачи (Tasks)

### Фаза A — Фундамент

**TASK-A01** — Инициализация проекта по команде из §2.
DoD: `npm run dev` запускается без ошибок, репозиторий инициализирован, `.gitignore` настроен.

**TASK-A02** — Создать структуру папок из §3 (пустые `index.ts`/`page.tsx`-заглушки там, где требуется валидный Next.js роут).
DoD: `npm run build` проходит на пустых страницах.

**TASK-A03** — Создать `styles/tokens.css` и `styles/glass.css` из §4, подключить в `app/layout.tsx`.
DoD: переменные видны в DevTools на `:root`.

**TASK-A04** — Создать `.env.example` с `NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api/v1` и `FEATURE_RECOMMENDATIONS=false`, `FEATURE_REVIEWS=false`. Скопировать в `.env.local`.
DoD: переменные читаются в `lib/feature-flags.ts` (создаётся в TASK-H01) без падения сборки.

**TASK-A05** — Реализовать `lib/api-client.ts`: экземпляр `axios` с `baseURL=process.env.NEXT_PUBLIC_API_BASE_URL`, интерсептор запроса (подставляет `Authorization: Bearer <access_token>` из стора авторизации), интерсептор ответа (на `401` — один раз `POST /auth/refresh`, при успехе повтор запроса, при провале — очистка токенов и редирект на `/login`; на любую ошибку — извлечение `detail` из тела в единый формат `ApiError`).
DoD: модуль не обращается к несуществующим эндпоинтам; покрыт юнит-тестом на сценарий refresh.

**TASK-A06** — Подключить `QueryClientProvider` (TanStack Query) в `app/layout.tsx` через `lib/query-client.ts`.
DoD: любой тестовый `useQuery` успешно резолвится в дев-режиме.

**TASK-A07** — Базовые UI-обёртки в `components/ui/`: `Button`, `Dialog`, `DropdownMenu`, `Tabs`, `Toast` на основе установленных Radix-примитивов, со стилями из `glass-surface` там, где это поверхность (Dialog, Toast, DropdownMenu — стеклянные; Button — нет).
DoD: каждый компонент имеет видимый focus-ring и работает без мыши (Tab/Enter/Esc).

**TASK-A08** — Компоненты `components/glass/`: `GlassCard`, `GlassPanel` (обёртки с классом `glass-surface` + `border-radius` токен), `LiquidBlobBackground` (2 SVG/CSS блоба `--bg-blob-violet` и `--bg-blob-cyan`, медленная анимация смещения `keyframes`, `will-change: transform`), `ShimmerSkeleton` (прямоугольник с shimmer-градиентом поверх `glass-surface`).
DoD: `LiquidBlobBackground` не вызывает просадки FPS ниже 50 на скролле (проверить DevTools Performance).

---

### Фаза B — Авторизация

**TASK-B01** — `types/auth.ts` с интерфейсами из §1.1.
DoD: типы используются (не `any`) во всех последующих B-задачах.

**TASK-B02** — `store/auth.ts` (Zustand): хранит `accessToken`, `user`, методы `setSession`, `clearSession`. `refreshToken` хранить в `httpOnly` cookie через Next.js Route Handler-обёртку логина/регистрации/рефреша (route handler сам делает запрос к backend и проксирует `access_token`/`user` в JSON-ответ клиенту, а `refresh_token` — в `httpOnly; Secure; SameSite=Lax` cookie).
DoD: `refresh_token` не виден в `localStorage`/JS (проверить в DevTools Application).

**TASK-B03** — `/login`: форма (React Hook Form + Zod), вызов `POST /auth/login` через route-handler-обёртку из TASK-B02, редирект на `/` при успехе, отображение ошибок `400`.
DoD: невалидный email/пароль блокируют сабмит до отправки на сервер.

**TASK-B04** — `/register`: форма с полями `email, username, password, password_confirm`, клиентская проверка совпадения паролей до сабмита, вызов `POST /auth/register`.
DoD: после успешной регистрации пользователь авторизован и видит баннер подтверждения почты (TASK-B08).

**TASK-B05** — `/forgot-password` → `/reset-password`: запрос сброса, переход по ссылке с `?token=`, проверка токена (`GET`), форма нового пароля (`POST`). Учесть rate-limit `5/час на IP, 5/час на email, 1/мин на email` — после отправки блокировать повтор кнопки на 60 сек с видимым таймером.
DoD: повторный клик в течение 60 сек невозможен на уровне UI (не только сервера).

**TASK-B06** — `/verify-email`: ввод кода, `POST /auth/verify_email?code=`; кнопка повторной отправки кода вызывает `POST /auth/send_verification`, учитывая лимиты `1/мин`, `3/день` — дизейблить кнопку с обратным отсчётом.
DoD: счётчик дневного лимита отражается в UI после 3-й попытки (кнопка скрыта/задизейблена до следующего дня).

**TASK-B07** — Подключить интерсептор `401` из TASK-A05 к стору из TASK-B02 (логаут при невозможности обновить токен).
DoD: истёкший access-токен в дев-инструментах приводит к автоматическому скрытому рефрешу без перезагрузки страницы.

**TASK-B08** — `components/layout/VerifyEmailBanner.tsx`: показывается глобально, если `useAuthMe()` → `is_verified === false`. Скрывается после подтверждения (рефетч `GET /auth/me`).
DoD: баннер не показывается неавторизованным пользователям.

**TASK-B09** — `/profile/sessions`: список через `GET /auth/sessions` (device/IP/страна), кнопки «Завершить» (одна) и «Завершить все, кроме текущей».
DoD: после завершения сессии список обновляется оптимистично и подтверждается рефетчем.

**TASK-B10** — Форма смены пароля в `/profile` через `PATCH /auth/password`, обновление токенов из ответа в сторе.
DoD: после смены пароля старый access-токен в сторе заменён новым без релогина.

---

### Фаза C — Каталог

**TASK-C01** — `types/movie.ts` из §1.2.
DoD: используется во всех C-задачах без `any`.

**TASK-C02** — Хуки в `features/movies/`: `useMovies(filters)`, `useMovie(id)`, `usePersons(search)`, `usePerson(id)`, `useGenres()`, `useStudios()`, `useCountries()` — все на TanStack Query, ключи кэша `["movies", filters]`, `["movie", id]` и т.д. Справочники (`genres/studios/countries`) — `staleTime: 24h`.
DoD: повторный вызов одного и того же хука с одинаковыми параметрами не делает повторного сетевого запроса (проверить Network).

**TASK-C03** — `components/movie/MovieCard.tsx`: постер, название, год, жанры (chip-список), кнопка-закладка (заглушка, реализуется в TASK-D02), hover-tilt по спецификации §4.
DoD: карточка корректно рендерится при отсутствии `poster_url` (плейсхолдер, не сломанная картинка).

**TASK-C04** — Главная `/`: `LiquidBlobBackground` + три блока:
  - «Новинки» — `useMovies({year_from: текущийГод - 1, limit: 12})`;
  - «Топ каталога» (НЕ «популярное» — у backend нет метрики популярности, не выдумывать сортировку) — `useMovies({limit: 12})` в порядке, который вернул backend;
  - «По жанрам» — для каждого жанра из `useGenres()` отдельный `useMovies({genre_id, limit: 10})`, рендер построчно.
DoD: ни один запрос не использует параметр, не перечисленный в §1.2.

**TASK-C05** — `/movies`: фильтры жанр/страна/студия/диапазон годов/поиск (ровно эти, без сортировки), пагинация (`page/limit`), синхронизация фильтров с query-string URL.
DoD: обновление страницы с заполненным URL восстанавливает те же фильтры.

**TASK-C06** — `/movies/[id]`: постер, описание, жанры/студии, списки `cast/directors/writers/producers`, `generateMetadata` с OpenGraph (см. TASK-I01 — связать после), слот-заглушка для `WatchProvidersRow` (реализуется в Фазе G) и слот-заглушка для рекомендаций/отзывов (Фаза H).
DoD: `404` от backend корректно рендерит Next.js `not-found.tsx`.

**TASK-C07** — `/persons/[id]`: био, фильмография (`movies` из ответа), слот для кнопки подписки (реализуется в TASK-D05).
DoD: пагинация фильмографии работает через `page` параметр у вложенного `movies`.

**TASK-C08** — `/search` + live-дропдаун в header: параллельный запрос `useMovies({search})` и `usePersons(search)`, дебаунс ввода `300ms`.
DoD: пустой запрос не вызывает сетевых вызовов.

---

### Фаза D — Избранное и подписки

**TASK-D01** — `features/favorites/useBookmarks.ts`: `GET /users/me/bookmarks` → `number[]`, затем `useQueries` с `["movie", id]` на каждый id (переиспользует кэш из TASK-C02).
DoD: при пустом списке закладок не выполняется ни одного лишнего запроса.

**TASK-D02** — `useToggleBookmark()` мутация: `POST/DELETE /users/me/bookmarks/{movie_id}` с optimistic update списка id. Подключить кнопку в `MovieCard` (TASK-C03) и на `/movies/[id]`.
DoD: при ошибке мутации UI откатывается к предыдущему состоянию (rollback).

**TASK-D03** — `/favorites`: рендер `MovieGrid` по данным из TASK-D01, пустое состояние с понятным сообщением и ссылкой на каталог.
DoD: страница доступна только авторизованным (редирект на `/login` иначе).

**TASK-D04** — `features/favorites/useSubscriptions.ts`: `GET /users/subscribe/person` + `useToggleSubscription()` (`POST/DELETE /users/subscribe/person/{id}`), optimistic update.
DoD: аналогично TASK-D02 — rollback при ошибке.

**TASK-D05** — Кнопка «Подписаться» на `/persons/[id]` (TASK-C07) на основе TASK-D04.
DoD: состояние кнопки (подписан/не подписан) верно восстанавливается при заходе на страницу.

**TASK-D06** — `/profile`: показать `username/email/role` из `GET /auth/me`; для `profile`/`history` — компонент `ComingSoonState` (создаётся в TASK-H02, здесь — заглушка-плейсхолдер до готовности).
DoD: страница не делает запрос к `Not implemented` эндпоинтам, если соответствующий feature-флаг выключен.

---

### Фаза E — Уведомления

**TASK-E01** — `types/notification.ts` из §1.4 + `lib/notification-mapping.ts`: словарь `type → {icon, defaultText, tone}` для `welcome/email_verification/password_reset/new_movie`.
DoD: для неизвестного будущего `type` есть безопасный fallback (нейтральная иконка, текст «Новое уведомление»).

**TASK-E02** — `features/notifications/useNotifications.ts`: `GET /notification` с `refetchInterval: 30000`; `useMarkRead`, `useMarkAllRead`, `useDeleteNotification` — все с optimistic update и инвалидацией счётчика непрочитанных.
DoD: после `markAllRead` бейдж непрочитанных обнуляется без ожидания следующего polling-тика.

**TASK-E03** — `components/layout/NotificationBell.tsx`: иконка с бейджем количества непрочитанных, открывает `DropdownMenu` (TASK-A07) с последними 5.
DoD: бейдж скрывается при 0 непрочитанных (не показывает «0»).

**TASK-E04** — `/notifications`: полный список с пагинацией, кнопки «прочитать», «прочитать все», «удалить» (удаление — через подтверждение в стеклянной плашке, не браузерный `confirm()`).
DoD: удаление недоступного (уже удалённого на сервере) уведомления не ломает UI — обрабатывается как «уже отсутствует», список тихо обновляется.

---

### Фаза F — Анимации и полировка (выполняется после Фаз A–E на готовом UI)

**TASK-F01** — Сигнатурный эффект `components/glass/LiquidLightLeak.tsx`: блок, следующий за курсором по формуле lerp из §4, оборачивается в Hero (`/`) и на `/movies/[id]`.
DoD: эффект отключается при `prefers-reduced-motion: reduce` (статичное положение).

**TASK-F02** — `useReducedMotion()` хук-обёртка над `window.matchMedia('(prefers-reduced-motion: reduce)')`, применить во ВСЕХ местах с Framer Motion/GSAP анимациями из Фаз A–E.
DoD: при включённой системной настройке ни одна анимация дольше `150ms` не воспроизводится.

**TASK-F03** — Scroll-reveal обёртка (`Framer Motion` + `useInView`) для карусели подборок и `MovieGrid`.
DoD: элементы за пределами вьюпорта не анимируются заранее (нет «прыжков» при быстром скролле).

**TASK-F04** — Переходы между страницами: `AnimatePresence` в `app/layout.tsx`, crossfade+blur `200–250ms` по спецификации §4.
DoD: навигация между `/movies` и `/movies/[id]` не показывает белый/чёрный «флеш» между страницами.

**TASK-F05** — Shared-element переход постера из `MovieCard` в `/movies/[id]` через `layoutId` (Framer Motion).
DoD: переход работает при прямом заходе по URL без перехода из списка (без `layoutId`, обычный fade).

**TASK-F06** — Анимация кнопки закладки (TASK-D02): морф иконки + короткая вспышка частиц при добавлении.
DoD: анимация не блокирует повторный клик (debounce, но не задержка реального запроса).

---

### Фаза G — Реферальная система «Где посмотреть» (только фронтенд, backend не трогать)

**TASK-G01** — `data/watch-providers.ts`: статический массив провайдеров.
```ts
export const watchProviders = [
  { id: "kinopoisk", name: "Кинопоиск HD", logoUrl: "/providers/kinopoisk.svg", brandColor: "#FF6B00",
    template: "https://hd.kinopoisk.ru/film/{externalId}?utm_source=goodfilms" },
  { id: "ivi", name: "ivi", logoUrl: "/providers/ivi.svg", brandColor: "#FFD400",
    template: "https://www.ivi.ru/watch/{externalId}?partner=goodfilms" },
  { id: "okko", name: "Okko", logoUrl: "/providers/okko.svg", brandColor: "#00C2FF",
    template: "https://okko.tv/movie/{externalId}?partner=goodfilms" },
  // START, Wink, KION, Premier — добавить по аналогии при наличии шаблонов affiliate-ссылок
] as const;
```
DoD: список не обращается к backend, используется только локально.

**TASK-G02** — `data/watch-links.json`: `{ "<movieId>": [{ "providerId": "ivi", "externalId": "12345", "accessType": "subscription" }] }`. Заполнить 5–10 примеров для тестовых фильмов из каталога.
DoD: файл валиден как JSON, читается без падения сборки.

**TASK-G03** — `app/watch-links/[movieId]/route.ts`: Route Handler, читает `watch-links.json` и `watch-providers.ts`, собирает финальные ссылки (подстановка `externalId` в `template`), отдаёт JSON `[{providerId, name, logoUrl, brandColor, url, accessType}]`.
DoD: для `movieId`, которого нет в `watch-links.json`, отдаёт `[]`, а не ошибку.

**TASK-G04** — `app/go/[providerId]/[movieId]/route.ts`: Route Handler, находит ссылку по `providerId+movieId`, логирует клик (минимально — `console.log`/файл; интеграция с Plausible — опционально по наличию ключа в `.env`), отдаёт `302 redirect` на финальный URL. Если ссылка не найдена — `404`.
DoD: прямой заход на `/go/ivi/999999` без существующей связки отдаёт `404`, а не редирект на `undefined`.

**TASK-G05** — `components/movie/WatchProvidersRow.tsx`: использует `GET /watch-links/{movieId}` (внутренний роут, не backend), рендерит ряд стеклянных «пилюль» с `logoUrl/brandColor`, `href="/go/{providerId}/{movieId}"`, `target="_blank" rel="nofollow sponsored noopener"`, подпись «Партнёрские ссылки» под блоком. Подключить в слот из TASK-C06.
DoD: если массив пуст — компонент не рендерит пустой контейнер (возвращает `null`).

---

### Фаза H — Заглушки и feature-флаги

**TASK-H01** — `lib/feature-flags.ts`: экспорт `FEATURE_RECOMMENDATIONS` и `FEATURE_REVIEWS` из `process.env`.
DoD: значения по умолчанию — `false`, если переменная не задана.

**TASK-H02** — `components/ui/ComingSoonState.tsx`: универсальный компонент «скоро доступно» с пропом `label`. Использовать для `/profile` (расширенные поля), истории просмотров, рекомендаций и отзывов при выключенном флаге.
DoD: единственный компонент используется во всех перечисленных местах (не дублировать вёрстку).

**TASK-H03** — Блок «Похожие фильмы» на `/movies/[id]` за `FEATURE_RECOMMENDATIONS`: при включении вызывает `GET /recommendations/movies/{id}/similar`; если ответ — заглушка (`Not implemented`), рендерит `ComingSoonState`, а не ошибку.
DoD: при выключенном флаге запрос вообще не выполняется.

**TASK-H04** — Блок «Отзывы и рейтинг» на `/movies/[id]` за `FEATURE_REVIEWS`, аналогично TASK-H03 с эндпоинтами `/reviews/movies/{id}` и `/reviews/movies/{id}/ratings`.
DoD: форма отправки отзыва скрыта при выключенном флаге целиком (не просто задизейблена).

---

### Фаза I — Качество, SEO, тесты

**TASK-I01** — `generateMetadata` для `/movies/[id]`: `title`, `description` (из `MovieDetail.description`, обрезанный до 160 символов), OpenGraph с `poster_url`, JSON-LD `<script type="application/ld+json">` со схемой `schema.org/Movie`.
DoD: валидация через Google Rich Results Test не выдаёт критических ошибок схемы.

**TASK-I02** — `app/sitemap.ts`: постранично обходит `GET /movies` (по `total/limit`), формирует `sitemap.xml` со всеми `/movies/[id]`.
DoD: `sitemap.xml` доступен и содержит реальные id из каталога, без дублей.

**TASK-I03** — `next.config.js`: `images.remotePatterns` под домен(ы) `poster_url`/`photo_url` из ответов backend.
DoD: `next/image` рендерит постеры без ошибки `hostname not configured`.

**TASK-I04** — Юнит-тесты (Vitest + RTL) на `useBookmarks`, `useNotifications`, интерсептор `api-client` (refresh-сценарий).
DoD: `npm run test` зелёный, покрытие критичных хуков ≥ 1 тест на happy-path + 1 на ошибку.

**TASK-I05** — Playwright E2E: регистрация → логин → добавление фильма в закладки → переход на `/favorites` → клик по партнёрской ссылке (мок `window.open`/проверка `href`).
DoD: сценарий проходит в CI без сетевых обращений к реальному backend (мок API через Playwright route).

**TASK-I06** — Lighthouse-аудит (`npm run lighthouse` или CI-степ): perf/seo/a11y ≥ 90.
DoD: отчёт сохранён как артефакт сборки; найденные проблемы либо исправлены, либо задокументированы как осознанный trade-off.

---

### Фаза J — Деплой

**TASK-J01** — `Dockerfile` (multi-stage, `output: "standalone"` в `next.config.js`).
DoD: `docker build` собирается, контейнер запускается и отвечает на `/`.

**TASK-J02** — Фрагмент для существующего `docker-compose` / Nginx Gateway-конфига, добавляющий фронтенд-сервис, проксируемый Gateway на `/` (не трогая существующие маршруты `/api/v1/**`).
DoD: фронтенд и существующий Gateway работают на разных путях без конфликтов маршрутизации.

**TASK-J03** — `README.md`: команды установки, `.env` переменные, команда запуска, команда тестов.
DoD: человек без контекста проекта может поднять окружение по одному README.

---

## 6. Итоговый порядок выполнения (граф зависимостей, краткая сводка)

```
A01→A02→A03→A04→A05→A06→A07→A08
A08 → B01..B10 (параллельно где нет внутренних зависимостей)
A08 → C01..C08
B02,C02 → D01..D06
A07 → E01..E04
(A–E завершены) → F01..F06
G01..G05 (независима от B–F, может выполняться параллельно после A08)
A04 → H01..H04
(весь функционал готов) → I01..I06 → J01..J03
```

Definition of Done всего проекта: все DoD-пункты задач выше выполнены, `npm run build`, `npm run test`, `npx playwright test` — зелёные, Lighthouse ≥ 90 по perf/seo/a11y.
