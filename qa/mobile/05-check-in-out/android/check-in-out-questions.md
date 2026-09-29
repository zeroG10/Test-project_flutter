# Check-In / Check-Out — Android: розбіжності й питання

Android-етап, recon A1 (2026-09-29, емулятор Pixel 7 · Android 16, debug-збірка): чим Android відрізняється від iOS
і від документів. Спільні рішення модуля — у [`../check-in-out-questions.md`](../check-in-out-questions.md); тут лише Android.
Модель оракула та сама: тести стверджують поведінку застосунку, розбіжність — питання, баг — лише зі слова власника.
Докази: `qa/shared/recon-2026-09-29-android.md`, дампи `qa/shared/recon-dumps/android-2026-09-29/`.

Статус: `відкрите` · `прийнято як є` · `баг`

## Розбіжності (D)

| # | Що | iOS | Android | Докази | Статус |
|---|---|---|---|---|---|
| D-CHIO-A1 | 🔴 «Підроблена» локація | симулятор **завжди** «підроблений» → потрібен службовий перемикач апки (Q-CHIO-5) | координати GPS емулятора (`adb emu geo fix`) — **чесні**: check-in проходить **без перемикача**. Справжній mock-провайдер (Appium Settings) → «Location could not be trusted» / Cancel / Got it | `confirm_check_in.xml`, `mock_location.xml` | відкрите |
| D-CHIO-A2 | Системний запит геолокації | Allow Once / Allow While Using App / Don't Allow | **While using the app / Only this time / Don't allow** + Precise / Approximate; після другої відмови — «більше не питати» | `perm_location.xml`, `perm_location_second.xml` | інфо |
| D-CHIO-A3 | Відмова в дозволі | «Location disabled» / … / Go to settings | **«Location access required»** / «GPS is required to check in. Enable location services to continue.» / Cancel / **Enable** (Enable знову показує системний запит). Це інший діалог коду апки (`showLocationAccessRequiredDialog`) | `location_disabled.xml` | відкрите |
| D-CHIO-A4 | «Точність локації» Google | — | системний діалог Google Play services «Location Accuracy» (No thanks / Turn on) перед першим визначенням — налаштування емулятора, увімкнено один раз | `gms_location_accuracy.xml` | інфо |
| D-CHIO-A5 | Без координат | не бачили | «Enter location manually» (див. D-ORDD-A5) — коли GPS не встиг; у тестах координати подаються кілька разів поспіль під час check-in | `location_manual_entry.xml` | інфо |
| D-CHIO-A6 | Решта потоку | — | «Confirm check in» / «Confirm check out», «You are not at the job site» (≈ 5.5 км), check-out → `completed` і джоба зникає зі списку — **як на iOS** | `confirm_check_*.xml`, `not_at_site.xml`, `after_check_out.xml` | інфо |

## Питання (Q)

| # | Питання | Рекомендація | Статус |
|---|---|---|---|
| Q-CHIO-A1 | На Android фікстура «на об'єкті» **не вмикає** службовий перемикач (він не потрібен); тест захисту від підробки — через mock-провайдер Appium (тимчасовий дозвіл `appops … mock_location allow`, у `finally` — назад). Ок? | так — це ближче до реального телефона, ніж на iOS | відкрите |
| Q-CHIO-A2 | Діалог відмови на Android інший (D-CHIO-A3) — прийняти як поведінку платформи, Android-колонка в карті `location-disabled` або окремий екран. Ок? | прийняти | відкрите |
