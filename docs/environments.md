# Environments and access — Concert Technologies Field Services (pointers only, NO secrets)

Filled by `/setup-project` from `setup/project.yaml` (`web.*`, `api.*`, `mobile.*` and the
Discovery profile `context.*` — prompts/00-discovery.md) and by hand after the kickoff.
Credentials live ONLY in the gitignored `.env` files (`automation/web/.env`,
`automation/mobile/.env`, `automation/api/.env`) — this file says *which variable*, never *the value*.

## Product

Мобільний застосунок на Flutter для **Field Technicians (FT)** — польових технічних
спеціалістів, що виконують монтаж і обслуговування обладнання на об'єктах замовника.
Замінює GoCanvas і CompanyCam. Бекенд: Order Management REST API (.NET + PostgreSQL)
та Survey Manager API (Node.js). Веб-панель використовує **Project Facilitator (PF)** —
**поза скоупом мобільної автоматизації**. У самій мобільній апці роль одна — FT
(SRS §2.3), тож матриці прав немає.

## Environments

| Env | Web | Mobile build | API | Purpose | Data reset |
|---|---|---|---|---|---|
| dev | `<WEB_BASE_URL>` | `automation/mobile/builds/<platform>/<file>` (source: `<where builds come from>`) | `<API_BASE_URL>` (spec: `docs/api/openapi.json`) | **automation target** | `<scheduled reset / seed script / none — ask>` |
| staging | | | | | |
| prod | — | — | — | never tested by automation (`.github/GATES.md` rule 4) | — |

Reachability note: `<is the target reachable from GitHub-hosted runners without VPN? checked YYYY-MM-DD>`.

## Roles and test accounts

| Role | Env vars | Can | Cannot |
|---|---|---|---|
| **Field Technician (FT)** — єдина роль у мобільній апці | `APP_USER_PHONE`, `APP_USER_EMAIL`, `APP_USER_OTP` в `automation/mobile/.env` | переглядати призначені замовлення, check-in / check-out, заповнювати опитування, додавати фото й нотатки, здавати результати | керувати замовленнями, призначати роботи — це робить PF через веб |
| Project Facilitator (PF) | — | керує замовленнями у веб-панелі | **поза скоупом** мобільної автоматизації |

> Record here any place where the UI names a role differently from the API — that is a
> product decision to test against, not a defect, once the team confirms it.

Login mechanics: **пароля в апці немає.** Вхід = номер телефону **або** email → 4-значний OTP
(SRS FR-LOG-05, FR-OTP-01). Канал OTP залежить від прапорця згоди на SMS (FR-012):
`TRUE` → SMS, `FALSE` → Email. **На DEV код захардкоджений** — змінна `APP_USER_OTP`,
тож читати пошту чи SMS не потрібно (підтверджено власником 2026-09-22).

Пастки, закладені в архітектуру тестів:
- `FR-OTP-13` — перевищення кількості спроб блокує акаунт на 2 хвилини;
- `FR-OTP-08/09` — новий код не запросити, доки не спливе відлік таймера.

Через це логін виконується **один раз на прогін**, далі тести працюють у відкритій сесії.
Account activation / password recovery: **не застосовується** — пароля немає, відновлювати
нічого. Реєстрація нового FT — окремий флоу (SRS §3.1.1.2) з верифікацією через OTP.
Поштовий ящик для автоматизації **не потрібен**, доки OTP на DEV захардкоджений.

## Browsers, devices, viewport

- Web: поза скоупом (`platforms.web: false` у `setup/project.yaml`).
- Mobile: `docs/platform-specs/supported-devices.md` (product policy) → `qa/shared/device-matrix/device-matrix.md` (what we test on).
- Ширина екрана за SRS §2.5: мін. **320px**, макс. **1440px**. Планшети — поза скоупом демо (рішення 2026-09-22).

## Known environment constraints (observed by automation)

`<Slow bundle, rate limiting, flaky endpoints, shared-DEV etiquette — with the date observed
and what the harness does about it (workers, timeouts). Retries stay 0 by policy.>`

## Test data and seeding

- Policy (`project.yaml → context.test_data.policy`): **`free`** on DEV — tests may create and delete
  their own data. Scheduled reset / seed script: none known.
- Endpoints usable for seeding/cleanup (from `docs/api/openapi.json`, recipe verified live —
  [docs/api/dev-test-data.md](api/dev-test-data.md)):
  - admin token: `POST /auth/sign-in` (`AuthController_signInWithEmailAndPass`), `API_ADMIN_*` in `automation/mobile/.env`;
  - jobs: `POST /job` with `userId` + `surveyId` → `DELETE /job/{id}` (`POST /job/assign/{phone}` is **not** used — it sends a CR-1 SMS link);
  - self-registered test users: `GET /technician?search=<email>` → `DELETE /user/full-delete/{user.id}` (`UserController_fullDelete`).
- Data rules (decisions 2026-09-22 / 2026-09-23 in [notes/decisions.md](notes/decisions.md)):
  - tests create and delete **only** their own jobs and users; surveys and the test technician are **read-only**;
  - unique markers: jobs `QA-AUTO-<stamp>`, users `qa-auto+<stamp>@example.com` + fictional phones
    `+1 202 555 01xx` (reserved ranges — no real person gets a message); the cleanup code refuses any other email;
  - cleanup at test end, pass or fail (`automation/mobile/fixtures/app_state.py`: fixture teardown), verified
    by a read-back; a failed cleanup is a harness error that names the record id for manual removal;
  - DEV-friendly: serial runs, one admin sign-in per run, one UI login per run where possible, at most one
    wrong OTP per run (FR-OTP-13 lockout), no load or stress tests.

## Open questions (answers go to `qa/shared/questions/` or the module's `*-questions.md`)

- Can test data be freely created and deleted on the target env? Does anyone else use it concurrently?
- Is there a scheduled DB reset or seed script?
- Which test accounts exist per role, and who owns them?
