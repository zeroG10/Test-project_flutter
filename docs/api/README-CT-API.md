# CT API — стан і придатність як джерело

## Що це

[`CT-API.postman_collection.json`](CT-API.postman_collection.json) — колекція «CT API»,
витягнута 2026-09-22 з публічної Postman-документації, на яку посилається SRS §1.5:
`https://documenter.getpostman.com/view/12140442/2sBXVhCqQB`

## ⚠️ Це ЧЕРНЕТКА, не контракт

Дослівно з опису колекції:

> This collection represents a **draft API plan** for the CT platform.
> The API is **not finalized** and should be treated as a **working specification**.
> Endpoint paths, request/response schemas, authentication logic, and flows **may change**.

**Наслідок для QA-доктрини:** ця колекція **не є оракулом**. Вона придатна для орієнтування
і для спроб підготувати дані, але жодне очікування не будується на ній без звірки з живим DEV.
Потрібен або актуальний OpenAPI/Swagger з бекенду, або підтвердження, що чернетка збігається
з реалізацією.

## Задокументовані ендпоінти (мобільна частина)

| Група | Метод і шлях | Призначення |
|---|---|---|
| Auth | `POST /auth/otp` | старт входу: `{phone, purpose: sign_in\|sign_up}` → OTP |
| Auth | `POST /auth/sign-in` | обмін `{otpId, code}` на access + refresh токени |
| Auth | `POST /auth/sign-up` · `sign-out` · `refresh-token` | реєстрація, вихід, оновлення токена |
| Jobs | `GET /jobs` · `GET /jobs/range` · `GET /jobs/:id` | список, діапазон дат, деталі |
| Jobs | `POST /jobs/check-in` | `{id, method: GPS, coordinates, horizontalAccuracyM, timestamp}` |
| Jobs | `POST /jobs/submit` | фінальна здача: `{id, checkIn?, survey[], photos[]}` |
| Jobs | `POST /jobs/redeem-code` | вхід за кодом із SMS-посилання |
| Jobs | `POST /jobs/:id/acknowledge` | підтвердження отримання |
| Files | `POST /files/upload` | завантаження фото |
| Notifications | `GET /notifications` · `PATCH /notifications/:id` · `POST\|DELETE /users/fcm-tokens` | сповіщення, push-токени |
| User | `GET\|PATCH\|DELETE /users/me` | профіль |
| Common | `GET /common/tags` | теги для фотозвіту |

## 🔴 Чого в API НЕМАЄ — і чому це важливо

**Немає жодного ендпоінта для створення або призначення замовлення.** Секція `Backend`
у колекції присутня, але **порожня** (`"item": []`).

Мобільний API вміє тільки *читати* замовлення і *діяти* по них. Призначає роботи Project
Facilitator через веб-систему. **Вирішено:** потрібні виклики є у Field Services API
(`docs/api/openapi.json`) — див. Q-006. Окрема зовнішня система **COPS** (онбординг
підрядників, SMS-згода, SRS §3.4.1) доступу не має і у скоуп не входить.

Чому це блокує повторні прогони: наскрізний сценарій **споживає** замовлення. Після
`check-in → робота → submit` замовлення завершене, і повторити на ньому той самий сценарій
не можна. Питання **Q-006** в `qa/shared/questions/open-questions.md`.

## Чого бракує для роботи

1. **`baseUrl` порожній** у колекції — потрібна DEV-адреса.
2. Актуальний Swagger/OpenAPI, якщо бекенд на .NET його віддає
   (зазвичай `/swagger/v1/swagger.json`) → класти в `docs/api/openapi.json`.
3. Відповідь на Q-006 про підготовку замовлень.

## Скоуп

API тут — **допоміжний інструмент для UI-тестів** (підготовка даних, логін в обхід OTP,
перевірка того, що дані доїхали після відправки через UI), а не окремий набір API-тестів.
`platforms.api` у `setup/project.yaml` поки не виставлений — рішення за власником.
