# Figma Sources — Mobile (Concert Technologies)

Карта дизайну для AI-агентів і QA: який Figma-файл описує мобільний застосунок і як
кожен екран співвідноситься з модулем у `qa/mobile/`. З цим файлом агенту не потрібне
свіже посилання — достатньо `fileKey` + `node-id` потрібного екрана.

## File

- **Name:** Concert Technologies: Mobile app (For review)
- **Platform:** Mobile — єдиний кросплатформний Flutter-застосунок
- **fileKey:** `eAb4RANWzBFgqiyiA5hUZ0`
- **URL:** https://www.figma.com/design/eAb4RANWzBFgqiyiA5hUZ0/Concert-Technologies--Mobile-app--For-review-
- **Остання зміна у Figma:** 2026-08-04
- **Базовий розмір макета:** 360×800 (телефон)

## Сторінки файлу

| Canvas | node-id | Що це | У скоупі? |
|---|---|---|---|
| Design Mobile app | `2451:73252` | Актуальний дизайн, секції **Light** і **Dark** | ✅ основне джерело |
| Admin panel | `2137:5932` | Веб-панель адміністратора (Managers, Field Technicians, Survey…) | ❌ інший продукт |
| Wireframes Mobile app | `2:3` | Ранні вайрфрейми | ❌ застаріле |

Секції теми всередині `Design Mobile app`:

| Тема | node-id |
|---|---|
| **Light** | `2451:82536` |
| **Dark** | `2451:83876` |

## Screen map — Light theme

Прив'язка до модулів з `qa/mobile/README.md`. Node-id вказано для секції або ключового екрана.

| Модуль | Код | Секція / екран | node-id |
|---|---|---|---|
| 01-splash | `SPL` | Splash & Wellcome | `2451:82537` |
| 01-splash | `SPL` | Spalsh animation | `2451:83867` |
| 02-authentication | `AUTH` | **Log in_Updated** (актуальна) | `3191:12921` |
| 02-authentication | `AUTH` | Log in_Updated → Log in | `3191:12922` |
| 02-authentication | `AUTH` | Log in_Updated → Log in_Error | `3191:12935` |
| ~~02-authentication~~ | `AUTH` | ~~Log in (стара версія)~~ — **поза скоупом**, рішення 2026-09-22 | `2671:14004` |
| 02-authentication | `AUTH` | **Registration_ Updated** (актуальна) | `3608:11989` |
| 02-authentication | `AUTH` | Phone number verification | `3608:11990` |
| 02-authentication | `AUTH` | Email Address verification | `3608:12035` |
| 02-authentication | `AUTH` | SMS Terms | `3608:12130` |
| ~~02-authentication~~ | `AUTH` | ~~Registration (стара версія)~~ — **поза скоупом**, рішення 2026-09-22 | `2671:13813` |
| 03-order-list | `ORDL` | Jobs_List view | `2451:82604` |
| 03-order-list | `ORDL` | Jobs_List view_Empty | `2451:83514` |
| 03-order-list | `ORDL` | Jobs_Calendar view | `2451:82613` |
| 03-order-list | `ORDL` | Jobs_Calendar view_empty | `2451:83469` |
| 04-order-details | `ORDD` | Jobs details_New | `2451:82657` |
| 04-order-details | `ORDD` | Jobs details_New_Updated | `2451:83368` |
| 04-order-details | `ORDD` | Job details_Atachments_Documents | `2451:83062` |
| 04-order-details | `ORDD` | Job details_Atachments_Photos | `2451:83346` |
| 04-order-details | `ORDD` | Job details_Atachments_Document details | `2451:83360` |
| 05-check-in-out | `CHIO` | Jobs details_New_Check in active | `2451:83418` |
| 05-check-in-out | `CHIO` | Job details_Confirm check in | `2451:83073` |
| 05-check-in-out | `CHIO` | Job details_Confirm check out | `2451:83083` |
| 05-check-in-out | `CHIO` | Job details_In progress_Check out | `2451:82844` |
| 06-order-progress | `ORDP` | Job details_In progress | `2451:82704` |
| 06-order-progress | `ORDP` | Job details_In progress_Scroll | `2451:83008` |
| 06-order-progress | `ORDP` | Job details_In progress_Poor connection | `2451:82898` |
| 07-submit-deliverables | `DLV` | Deliverables item | `4009:12423` |
| 07-submit-deliverables | `DLV` | Job details_In progress_Success submit | `2451:82953` |
| 08-survey | `SRV` | survey (секція) | `4009:12410` |
| 08-survey | `SRV` | Survey | `4009:12520` |
| 08-survey | `SRV` | Survey_Filled | `4009:12675` |
| 09-photo-report | `PHR` | Photo report | `2451:83093` |
| 09-photo-report | `PHR` | Photo report_Add photo | `2451:83162` |
| 09-photo-report | `PHR` | Photo report_Description & Tags | `2451:82758` |
| 09-photo-report | `PHR` | Manage photo | `2451:83195` |
| 09-photo-report | `PHR` | Manage photo_Markup | `2451:83211` |
| 09-photo-report | `PHR` | Manage photo_Crop | `2451:83225` |
| 10-notes | `NOTE` | Note | `2451:83105` |
| 10-notes | `NOTE` | Notes_Add note | `2451:83128` |
| 10-notes | `NOTE` | Notes_Add note_Filled | `2451:83136` |
| 10-notes | `NOTE` | Notes_Edit note | `2451:83144` |
| 11-notifications | `NOTIF` | Notifications | `2451:83820` |
| 12-profile | `PRF` | Profile | `2453:10667` |
| — (крос-модульне) | | No internet connection_Screen | `2451:83554` |
| — (крос-модульне) | | Snackbar-и, діалоги, date/dial picker | у секції Jobs `2451:82554` |

## Як агенти це читають

Через локальний MCP-сервер `figma` (PAT у `FIGMA_PERSONAL_ACCESS_TOKEN`, див. `.mcp.json`):
- структура й контент: `mcp__figma__get_figma_data` з `fileKey` + `nodeId`;
- зображення: `mcp__figma__download_figma_images`.

Прямий доступ без MCP (напр. зі скрипта):
`curl -H "X-Figma-Token: $FIGMA_PERSONAL_ACCESS_TOKEN" "https://api.figma.com/v1/files/eAb4RANWzBFgqiyiA5hUZ0/nodes?ids=<node-id>&depth=2"`

## ⚠️ Відкриті питання до власника (блокують візуальні очікування)

1. ~~**Дубльовані версії екранів.**~~ ✅ **ВИРІШЕНО 2026-09-22** (власник: mykola.zhuchenko):
   актуальні — **`Log in_Updated`** (`3191:12921`) і **`Registration_ Updated`** (`3608:11989`).
   Старі секції `Log in` / `Registration` виведені зі скоупу. Див. `docs/notes/decisions.md`.
2. **Темна тема.** У дизайні є повна секція **Dark** (`2451:83876`), але в чеклісті
   згадок про темну тему немає. Апка її підтримує? Якщо так — це окремий вимір покриття.
3. ~~**Планшети.**~~ ✅ **ВИРІШЕНО 2026-09-22**: поза скоупом демо. Колонка `Tablet` —
   ті самі перевірки на планшеті, окремих макетів немає (усі 360×800). Цільова матриця:
   телефони iOS + Android. Планшет підключається пізніше як ще одна конфігурація.

Усі три питання закриті — див. `docs/notes/decisions.md`. Нові фіксуються там само і в `qa/mobile/<модуль>/<модуль>-questions.md`.
